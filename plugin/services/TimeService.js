var omniService = angular.module("OmniWheel.Services")

omniService.factory('TimeService', function ($rootScope, socket) {
    var service = {}

    service.formatTime = function(d) {
        date = new Date(d)
        return date.getDate()+ '/' + (date.getMonth()+1) + '/'+ date.getFullYear()
    }

    return service
})