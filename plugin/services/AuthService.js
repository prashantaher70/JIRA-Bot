var omniService = angular.module("OmniWheel.Services")

omniService.factory('AuthService', function ($rootScope, socket) {
    var service = {}

    service.startAuth = function(orgName, userId, configuring) {

        return new Promise(function(resolve, reject) {
            var data = {
                'orgName': orgName,
                'userId': userId,
                'configuring': configuring
            }
            socket.emit("AUTH_start_auth", data)
            socket.on("AUTH_start_auth_response", function(d) {
                resp = d

                if(resp.error) {
                    reject(resp)
                } else {
                    chrome.storage.local.set({"user": resp.data}, function() {
                        resolve(resp)
                    })
                }
            })
        })
    }

    service.continueAuth = function(userId) {
        return new Promise(function(resolve, reject){
            var data = {
                'userId': userId
            }

            socket.emit("AUTH_continue_auth", data)
            socket.on("AUTH_continue_auth_response", function(d) {
                resp = d

                console.log(resp)
                if(resp.error) {
                    reject(resp)
                } else {
                    resolve(resp)
                }
            })
        })
    }

    service.syncUserAndSetupWebhook = function(userId, setupWebhook) {
        return new Promise(function(resolve, reject){
            var data = {
                'userId': userId,
                'setupWebhook': setupWebhook
            }

            socket.emit("AUTH_sync_user_set_webhook", data)
            socket.on("AUTH_sync_user_set_webhook_response", function(d) {
                resp = d

                if(resp.error) {
                    reject(resp)
                } else {
                    resolve(resp)
                }
            })
        })
    }

    service.createOrg = function(orgName, orgJiraEndpoint) {
        return new Promise(function(resolve, reject){
            var data = {
                'orgName': orgName,
                'orgJiraEndpoint': orgJiraEndpoint
            }

            socket.emit("AUTH_create_org", data)
            socket.on("AUTH_create_org_response", function(d) {
                resp = d

                if(resp.error) {
                    reject(resp)
                } else {
                    var user = {
                        'orgName': orgName
                    }

                    chrome.storage.local.set({"user": user}, function() {
                        resolve(resp)
                    })
                }
            })
        })
    }

    service.getUser = function() {
        return new Promise(function(resolve, reject) {
            chrome.storage.local.get("user", function (data) {
                if(data.user != undefined) {
                    resolve(data.user)
                } else {
                    r = {
                        'error': true,
                        'errorCode': 401,
                        'errorMessage': 'Not logged in'
                    }
                    reject(r)
                }
            })
        });
    }


    service.onError = function(callback) {
        socket.on("connect_error", function(err) {
            callback("Unable to contact server")
        })

        socket.on("connect_timeout", function(err) {
            callback("Unable to contact server")
        })

        socket.on('reconnect', function(attemptNumber) {
        })

        socket.on('reconnect_error', function(err) {
        })

        socket.on('error', function(err) {
            callback("Unable to contact server")
        })

    }

    return service
})