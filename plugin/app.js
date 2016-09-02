omni = angular.module('OmniWheel', [
  'ngRoute',
  'ngMaterial',
  'ui.router',
  'OmniWheel.Services',
  'Scope.safeApply'
], function($compileProvider){
     $compileProvider.imgSrcSanitizationWhitelist(/^\s*(https?|ftp|file|chrome-extension|blob:chrome-extension):|data:image\//);
     $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|file|chrome-extension):/);
})
.config(config)
.run(run)


 config.$inject = [
    '$stateProvider',
    '$locationProvider',
    '$urlRouterProvider',
    '$mdThemingProvider',
    '$mdIconProvider'
 ]
 function config($stateProvider,
                     $locationProvider,
                     $urlRouterProvider,
                     $mdThemingProvider,
                     $mdIconProvider) {

    $urlRouterProvider.otherwise('/home')

    $stateProvider
        .state('onboard', {
            url: '/',
            templateUrl: '/views/onboard.html',
            controller: 'OnboardController'
        })
        .state('voice', {
            url: '/voice',
            templateUrl: '/views/voice.html'
        })
        .state('home', {
            url: '/home',
            templateUrl: '/views/home.html',
            controller: 'HomeController'
        })

    $mdThemingProvider.theme('default');
 }


 run.$inject = ['$rootScope', '$location', '$state'];
 function run($rootScope, $location, $state) {

     function message(toState, toParams, fromState, fromParams) {
         return fromState.name + angular.toJson(fromParams) +
         ' -> ' + toState.name + angular.toJson(toParams);
     }

     // Check invalid state change
     $rootScope.$on('$stateChangeStart', function (event, toState, toParams,
        fromState, fromParams) {

     });


     $rootScope.$on('$stateChangeSuccess', function (event, toState, toParams,
        fromState, fromParams) {

         console.log('Success: ' + message(toState, toParams, fromState, fromParams));
     });

     $rootScope.$on('$stateChangeError', function (event, toState, toParams, fromState,
        fromParams, error) {
         //console.log('Error:   ' + message(toState, toParams, fromState, fromParams), error);
     });
 }