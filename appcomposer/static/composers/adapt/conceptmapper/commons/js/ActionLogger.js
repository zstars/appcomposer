// Generated by CoffeeScript 1.6.3
(function() {
  "use strict";
  var _base, _base1,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  if (window.ut == null) {
    window.ut = {};
  }

  if ((_base = window.ut).commons == null) {
    _base.commons = {};
  }

  if ((_base1 = window.ut.commons).actionlogging == null) {
    _base1.actionlogging = {};
  }

  window.ut.commons.actionlogging.ActionLogger = (function() {
    function ActionLogger() {
      this.log = __bind(this.log, this);
      this.setProvider = __bind(this.setProvider, this);
      this.setGenerator = __bind(this.setGenerator, this);
      this.setTarget = __bind(this.setTarget, this);
      console.log("Initializing ActionLogger");
      console.log("...setting default logging target: nullLogging.");
      this.loggingTarget = this.nullLogging;
      this.actorId = "unknownActorId";
      this.target = {
        "objectType": "unknownType",
        "id": "00000000-0000-0000-0000-000000000000",
        "displayName": "unnamed"
      };
      this.generator = {
        "objectType": "unknownType",
        "url": "unknown",
        "id": "00000000-0000-0000-0000-000000000000"
      };
      this.provider = {
        "objectType": "unknownType",
        "id": "00000000-0000-0000-0000-000000000000"
      };
    }

    ActionLogger.prototype.setActorId = function(newActorId) {
      return this.actorId = newActorId;
    };

    ActionLogger.prototype.setLoggingTarget = function(newLoggingTarget) {
      return this.loggingTarget = newLoggingTarget;
    };

    ActionLogger.prototype.setTarget = function(newTarget) {
      return this.target = newTarget;
    };

    ActionLogger.prototype.setGenerator = function(newGenerator) {
      return this.generator = newGenerator;
    };

    ActionLogger.prototype.setProvider = function(newProvider) {
      return this.provider = newProvider;
    };

    ActionLogger.prototype.setLoggingTargetByName = function(newLoggingTargetName) {
      console.log("ActionLogger: setting logging target (by name) to " + newLoggingTargetName);
      if (newLoggingTargetName === "null") {
        return this.loggingTarget = this.nullLogging;
      } else if (newLoggingTargetName === "console") {
        return this.loggingTarget = this.consoleLogging;
      } else if (newLoggingTargetName === "consoleShort") {
        return this.loggingTarget = this.consoleLoggingShort;
      } else if (newLoggingTargetName === "dufftown") {
        return this.loggingTarget = this.dufftownLogging;
      } else if (newLoggingTargetName === "opensocial") {
        return this.loggingTarget = this.opensocialLogging;
      } else {
        console.log("ActionLogger: unknown logging target, setting to 'null'");
        return this.loggingTarget = this.nullLogging;
      }
    };

    ActionLogger.prototype.log = function(verb, object) {
      var activityStreamObject, actorObject;
      activityStreamObject = {};
      activityStreamObject.published = new Date().toISOString();
      actorObject = {};
      actorObject.id = this.actorId;
      actorObject.objectType = "person";
      activityStreamObject.actor = actorObject;
      activityStreamObject.verb = verb;
      activityStreamObject.object = object;
      activityStreamObject.target = this.target;
      activityStreamObject.generator = this.generator;
      activityStreamObject.provider = this.provider;
      return this.loggingTarget(activityStreamObject);
    };

    ActionLogger.prototype.nullLogging = function(action) {};

    ActionLogger.prototype.consoleLogging = function(activityStreamObject) {
      return console.log(JSON.stringify(activityStreamObject, void 0, 2));
    };

    ActionLogger.prototype.consoleLoggingShort = function(activityStreamObject) {
      return console.log("ActionLogger: " + activityStreamObject.verb + " " + activityStreamObject.object.objectType + ", id: " + activityStreamObject.object.id);
    };

    ActionLogger.prototype.opensocialLogging = function(activityStreamObject) {
      var logObject;
      if (osapi !== void 0) {
        logObject = {
          "userId": "@viewer",
          "groupId": "@self",
          activity: activityStreamObject
        };
        console.log("ActionLogger: logging to Graasp: " + activityStreamObject.verb + " " + activityStreamObject.object.objectType + ", id: " + activityStreamObject.object.id);
        return osapi.activitystreams.create(logObject).execute(function(response) {
          if (response.id !== void 0) {
            return console.log("ActionLogger: sucessfully logged via osapi, response.id: " + response.id);
          } else {
            console.log("ActionLogger: something went wrong when logging via osapi:");
            return console.log(response);
          }
        });
      } else {
        return console.log("ActionLogger: can't log, osapi is undefined.");
      }
    };

    ActionLogger.prototype.dufftownLogging = function(activityStreamObject) {
      console.log("ActionLogger: logging to go-lab.collide.info: " + activityStreamObject.verb + " " + activityStreamObject.object.objectType + ", id: " + activityStreamObject.object.id);
      return $.ajax({
        type: "POST",
        url: "http://go-lab.collide.info/activity",
        data: JSON.stringify(activityStreamObject),
        contentType: "application/json",
        success: function(responseData, textStatus, jqXHR) {
          return console.log("POST actionlog success, response: " + responseData.statusText);
        },
        error: function(responseData, textStatus, errorThrown) {
          return console.log("POST actionlog failed, response: " + responseData.statusText);
        }
      });
    };

    return ActionLogger;

  })();

}).call(this);

/*
//@ sourceMappingURL=ActionLogger.map
*/