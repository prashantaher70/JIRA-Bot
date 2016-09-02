omni = angular.module("OmniWheel")

omni.controller('HomeController', ['AuthService', '$state', '$scope', 'socket', '$timeout', '$mdToast', 'ApiService', '$http',
    'TimeService', function(AuthService, $state, $scope, socket, $timeout, $mdToast, ApiService, $http, TimeService){

    vm = $scope;
    vm.events = []
    vm.TimeService = TimeService

    socket.on("connect", function(){
        AuthService.getUser()
            .then(function(user){
                socket.emit("AUTH_set_user_context", user.userId)
            })
            .catch(function() {
                vm.initialise()
            })
    })

    vm.resetCommandFlow = function() {
        vm.askAttrs = undefined
        vm.answer = undefined
        vm.ask = false
        vm.showAnswer = false
    }

    vm.finishedSpeaking = function(transcript) {
        vm.resetCommandFlow()
        socket.emit("command_request", transcript)
    }

    vm.submitAskResponse = function() {
        vm.resetCommandFlow()
        socket.emit("ask_response", vm.askResponse)
    }

    socket.on("command_response", function(answer) {
        console.log(answer)
        if(answer.error) {
            handleError(answer)
        } else{
            vm.answer = answer
            vm.showAnswer = true
        }
    })

    socket.on("ask", function(attrs) {
        vm.askResponse = {}
        vm.askAttrs = attrs
        vm.ask = true
    })

    function loadAvatar(e) {
        return new Promise(function(resolve, reject) {
            e.user.avatarObject = ""
            $http.get(e.user.avatar, {responseType: "blob"})
                .success(function(data, status, headers, config) {
                    e.user.avatarObject = window.URL.createObjectURL(data)
                    resolve()
                })
                .error(function(data, status, headers, config) {
                    reject()
                })
        })
    }

    vm.loadNotifications = function() {
        vm.events = []

         ApiService.loadNotifications()
            .then(function(resp) {
                resp.data.forEach(function(v){
                    loadAvatar(v).then(function() {})
                })
                vm.events = resp.data
            })
            .catch(function(resp) {
                handleError(resp)
            })
    }

    socket.on('set_user_context_response', function(d) {
        //initialise app now. Context is all set
        vm.initialise()
    })

    vm.initialise = function() {
        vm.loadNotifications()
    }

    function notify(event) {
        var title = 'Update on ' + event.issue.key
        var body = event.user.displayName + ' ' + event.action + ' ' + event.issue.summary + ' '+ event.object
        var id = new Date(event.timestamp)

        chrome.notifications.create(id.toString(), {
            type: 'basic',
            iconUrl: event.user.avatarObject,title,
            message: body,
            title: title
        }, function(){})

        setTimeout(function(){
            chrome.notifications.clear(id.toString());
        },12000);
    }

    socket.on("notification", function(e) {
        loadAvatar(e)
            .then(function() {
                notify(e)
            })
        vm.events.unshift(e)
    })

    vm.openLink = function(link) {
        window.open(link)
    }

    function showError(msg) {
        $mdToast.show(
            $mdToast.simple()
            .textContent(msg)
            .hideDelay(3000)
        )
    }

    AuthService.onError(showError)

    function handleError(data) {
        if(data.error && data.errorCode == 401) {
            showError('Not logged in Redirecting...')
            $timeout(function() {
                $state.go('onboard')
            }, 3000)
            return
        }
        if(data.error) {
           showError(data.errorMessage)
           return
        }
    }
}])