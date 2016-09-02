var omniService = angular.module("OmniWheel.Services")

omniService.factory('socket', function ($rootScope) {
  var socket = io.connect('http://example.com', {
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        timeout: 10000,
        reconnectionAttempts: 1000
  })

  return {
    on: function (eventName, callback) {
      socket.on(eventName, function () {
        console.log('Got: ' + eventName)
        var args = arguments;
        $rootScope.$apply(function () {
          callback.apply(socket, args);
        });
      });
    },
    emit: function (eventName, data, callback) {
      console.log('Sending: ' + eventName)
      socket.emit(eventName, data, function () {
        var args = arguments;
        $rootScope.$apply(function () {
          if (callback) {
            callback.apply(socket, args);
          }
        });
      })
    }
  };
});