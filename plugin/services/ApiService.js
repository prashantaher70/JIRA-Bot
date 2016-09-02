var omniService = angular.module("OmniWheel.Services")

omniService.factory('ApiService', function ($rootScope, socket) {
    var service = {}

    service.getJira = function(jira) {
        return new Promise(function(resolve, reject){
            var data = {
                'issue': jira
            }

            socket.emit("AUTH_get_jira", data)
            socket.on("AUTH_get_jira_response", function(d) {
                resp = d

                if(resp.error) {
                    reject(resp)
                } else {
                    resolve(resp)
                }
            })
        })
    }

    service.loadNotifications = function() {
        return new Promise(function(resolve, reject){
            var data = {
            }

            socket.emit("load_notifications", data)
            socket.on("load_notifications_response", function(d) {
                resp = d

                if(resp.error) {
                    reject(resp)
                } else {
                    resolve(resp)
                }
            })
        })
    }

    return service
})