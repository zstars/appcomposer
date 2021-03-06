#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

from flask import request, render_template, flash, json, url_for, redirect

from appcomposer import db
from appcomposer.appstorage.api import get_app, update_app_data, add_var
from appcomposer.babel import gettext
from appcomposer.composers.translate import translate_blueprint
from appcomposer.composers.translate.bundles import BundleManager, Bundle
from appcomposer.composers.translate.db_helpers import _db_get_lang_owner_app, _db_declare_ownership
from appcomposer.composers.translate.updates_handling import on_leading_bundle_updated
from appcomposer.csrf import verify_csrf
from appcomposer.login import requires_login


@translate_blueprint.route("/edit", methods=["GET", "POST"])
@requires_login
def translate_edit():
    """
    Translation editor for the selected language.

    @note: Returns error 400 if the source language or group don't exist.
    """

    # No matter if we are handling a GET or POST, we require these parameters.
    appid = request.values.get("appid")
    srclang = request.values.get("srclang")
    targetlang = request.values.get("targetlang")
    srcgroup = request.values.get("srcgroup")
    targetgroup = request.values.get("targetgroup")

    # Retrieve the application we want to view or edit.
    app = get_app(appid)
    if app is None:
        return render_template("composers/errors.html", message=gettext("App not found")), 404

    bm = BundleManager.create_from_existing_app(app.data)
    spec = bm.get_gadget_spec()

    # Retrieve the bundles for our lang. For this, we build the code from the info we have.
    srcbundle_code = BundleManager.partialcode_to_fullcode(srclang, srcgroup)
    targetbundle_code = BundleManager.partialcode_to_fullcode(targetlang, targetgroup)

    srcbundle = bm.get_bundle(srcbundle_code)

    # Ensure the existence of the source bundle.
    if srcbundle is None:
        return render_template("composers/errors.html",
                               message=gettext("The source language and group combination does not exist")), 400

    targetbundle = bm.get_bundle(targetbundle_code)

    # The target bundle doesn't exist yet. We need to create it ourselves.
    if targetbundle is None:
        splits = targetlang.split("_")
        if len(splits) == 2:
            lang, country = splits
            targetbundle = Bundle(lang, country, targetgroup)
            bm.add_bundle(targetbundle_code, targetbundle)

    # Get the owner for this target language.
    owner_app = _db_get_lang_owner_app(spec, targetlang)

    # If the language has no owner, we declare ourselves as owners.
    if owner_app is None:
        _db_declare_ownership(app, targetlang)
        owner_app = app

    # We override the standard Ownership's system is_owner.
    # TODO: Verify that this doesn't break anything.
    is_owner = owner_app == app

    # Get the language names
    target_translation_name = targetbundle.get_readable_name()
    source_translation_name = srcbundle.get_readable_name()

    # This is a GET request. We are essentially viewing-only.
    if request.method == "GET":
        pass

    # This is a POST request. We need to save the entries.
    else:

        # Protect against CSRF attacks.
        if not verify_csrf(request):
            return render_template("composers/errors.html",
                                   message=gettext("Request does not seem to come from the right source (csrf check)")), 400

        # Retrieve a list of all the key-values to save. That is, the parameters which start with _message_.
        messages = [(k[len("_message_"):], v) for (k, v) in request.values.items() if k.startswith("_message_")]

        # Save all the messages we retrieved from the POST or GET params into the Bundle.
        for identifier, msg in messages:
            if len(msg) > 0:  # Avoid adding empty messages.
                targetbundle.add_msg(identifier, msg)

        # Now we need to save the changes into the database.
        json_str = bm.to_json()
        update_app_data(app, json_str)

        flash(gettext("Changes have been saved."), "success")

        propose_to_owner = request.values.get("proposeToOwner")
        if propose_to_owner is not None and owner_app != app:

            # Normally we will add the proposal to the queue. However, sometimes the owner wants to auto-accept
            # all proposals. We check for this. If the autoaccept mode is enabled on the app, we do the merge
            # right here and now.
            obm = BundleManager.create_from_existing_app(owner_app.data)
            if obm.get_autoaccept():
                flash(gettext("Changes are being applied instantly because the owner has auto-accept enabled"))

                # Merge into the owner app.
                obm.merge_bundle(targetbundle_code, targetbundle)

                # Now we need to update the owner app's data. Because we aren't the owners, we can't use the appstorage
                # API directly.
                owner_app.data = obm.to_json()
                db.session.add(owner_app)
                db.session.commit()

                # [Context: We are not the leading Bundles, but our changes are merged directly into the leading Bundle]
                # We report the change to a "leading" bundle.
                on_leading_bundle_updated(spec, targetbundle)

            else:

                # We need to propose this Bundle to the owner.
                # Note: May be confusing: app.owner.login refers to the generic owner of the App, and not the owner
                # we are talking about in the specific Translate composer.
                proposal_data = {"from": app.owner.login, "timestamp": time.time(), "bundle_code": targetbundle_code,
                                 "bundle_contents": targetbundle.to_jsonable()}

                proposal_json = json.dumps(proposal_data)

                # Link the proposal with the Owner app.
                add_var(owner_app, "proposal", proposal_json)

                flash(gettext("Changes have been proposed to the owner"))

        # If we are the owner app.
        if owner_app == app:
            # [Context: We are the leading Bundle]
            # We report the change.
            on_leading_bundle_updated(spec, targetbundle)

        # Check whether the user wants to exit or to continue editing.
        if "save_exit" in request.values:
            return redirect(url_for("user.apps.index"))




    return render_template("composers/translate/edit.html", is_owner=is_owner, app=app, srcbundle=srcbundle,
                           targetbundle=targetbundle, spec=spec, target_translation_name=target_translation_name,
                           source_translation_name=source_translation_name)
