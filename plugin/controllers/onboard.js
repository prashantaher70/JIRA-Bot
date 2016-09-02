omni = angular.module("OmniWheel")

omni.controller('OnboardController', ['AuthService', '$state', '$scope', '$mdToast',
    function(AuthService, $state, $scope, $mdToast){
    vm =$scope

    function showError(msg) {
        $mdToast.show(
            $mdToast.simple()
            .textContent(msg)
            .hideDelay(3000)
        )
    }

    AuthService.onError(showError)

    vm.init = function() {
        AuthService.getUser().then(function(user){
            vm.user = user
            vm.startAuth(user.orgName, user.userId, false)
        }, function(error){

        })
    }

    vm.init()

    vm.loginData = {
        'orgName': null
    }

    vm.setupWebhook = false

    vm.createOrgData = {
        'orgName': null,
        'orgJiraEndpoint': null
    }


    vm.register = function() {
        vm.currentPage = 'Register_Fill_Org_Details'
    }

    vm.createOrg = function() {
        AuthService.createOrg(vm.createOrgData.orgName, vm.createOrgData.orgJiraEndpoint)
            .then(function() {
                vm.setupWebhook = true
                vm.currentPage = 'Register_Configure_Jira'
            })
            .catch(function(resp){
                vm.handleServerError(resp)
            })
    }

    vm.startAuthAfterConfig = function() {
        AuthService.getUser()
            .then(function(user) {
                vm.startAuth(user.orgName, user.userId, true)
            })
            .catch( function(error) {

            })
    }

    vm.login = function() {
        //save orgName and startAuth
        vm.setupWebhook = false
        vm.startAuth(vm.loginData.orgName, null, false)
    }

    vm.startAuth = function(orgName, userId, adminTriggered) {
        //send orgName and token
        AuthService.startAuth(orgName, userId, adminTriggered)
            .then(function(data) {
                return AuthService.getUser()
            })
            .then(function(user) {
                $scope.$safeApply(function() {
                    vm.user = user
                    vm.currentPage = 'AuthUrlPrintStep'
                })
            }).catch( function(resp) {
                if(resp.error && resp.errorCode == 401) {
                    //TODO: is not admin triggered, ask admin to configure
                    //TODO: if admin, ask to check config
                    showError(resp.errorMessage)
                    return
                }
                if(resp.error) {
                    //TODO: Retry same action
                    showError(resp.errorMessage)
                    return
                }
            })
    }

    vm.continueAuth = function() {
        AuthService.getUser()
            .then(function(user){
                console.log("Continuing auth")
                return AuthService.continueAuth(user.userId)
            })
            .then(function(data) {
                //update progress
                return vm.synUserAndSetupWebhook()
            })
            .then(function() {
                $state.go("home")
            })
            .catch(function(resp){
                vm.handleServerError(resp)
            })
    }

    vm.synUserAndSetupWebhook = function() {
        return new Promise(function(resolve, reject) {
            //get user Id, sync user and setup webhook
            AuthService.getUser()
                .then(function(user){
                    console.log("Setting up webhook and syncing user")
                    return AuthService.syncUserAndSetupWebhook(user.userId, vm.setupWebhook)
                })
                .then(function(data){
                    resolve()
                })
                .catch(function(e){
                    reject(e)
                })
        })
    }

    vm.handleServerError = function(data) {
        if(data.error && data.errorCode == 401) {
            //TODO: start Auth as user had rejected, token expired or token reused somehow
            showError(data.errorMessage)
            return
        }
        if(data.error) {
            //TODO: Retry same action
            showError(data.errorMessage)
            return
        }
    }

    vm.openWindow = function() {
        window.open(vm.user.authUrl, "OmniOAuthWindow",
        "toolbar=no,scrollbars=no,resizable=no,width=400,height=400");
    }

    if(!String.prototype.trim) {
        String.prototype.trim = function () {
            return this.replace(/^\s+|\s+$/g,'');
        };
    }

    var setClipboardData = function(data) {
        var copyListener = function(event) {
            document.removeEventListener("copy", copyListener);
            event.preventDefault();
            event.clipboardData.items.add(data, "text/plain");
        };

        document.addEventListener("copy", copyListener);
        document.execCommand("copy");
    }

    vm.copyToClipboard = function(event) {
        var publicKey = document.querySelector('.js-public-key')
        setClipboardData(publicKey.textContent.trim())
    }
}])