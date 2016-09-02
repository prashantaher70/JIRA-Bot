var omniService = angular.module("OmniWheel")

omniService.directive('omniComments', function($http, TimeService) {
    var directive = {};

    directive.restrict = 'E';

    directive.replace = true;

    directive.template = ''
                    + '<div layout="row">'
                    +       '<div flex="100" ng-if="initialised">'
                    +           '<div layout="column">'
                    +               '<div layout="row" ng-repeat="comment in comments">'
                    +                   '<div>'
                    +                       '<p><img ng-src="{{comment.author.avatarObject}}" class="md-avatar" alt="{{comment.author.displayName}}"/> </p>'
                    +                   '</div>'
                    +                   '<div style="margin-left:8px" layout="column">'
                    +                       '<h3 style="margin-bottom:2px;">{{comment.author.displayName}}</h3>'
                    +                       '<p style="margin-bottom:4px; margin-top:2px;">{{comment.body}}</p>'
                    +                       '<div><code>{{TimeService.formatTime(comment.updated)}}</code></div>'
                    +                   '</div>'
                    +               '</div>'
                    +           '</div>'
                    +       '</div>'
                    + '</div>'

    directive.scope = {
            comments: '='
    };

    directive.link = function(scope, elem, attr) {
        scope.initialised = false

        function loadAvatar(comment) {
            return new Promise(function(resolve, reject) {
                comment.author.avatarObject = ""
                $http.get(comment.author.avatarUrls["48x48"], {responseType: "blob"})
                    .success(function(data, status, headers, config) {
                        comment.author.avatarObject = window.URL.createObjectURL(data)
                        resolve()
                    })
                    .error(function(data, status, headers, config) {
                        reject()
                    })
            })
        }

        scope.$watch(function() {
            return scope.comments
        }, function(n,o) {
            if(scope.comments != undefined && scope.comments != null && scope.comments != []) {
                scope.initialised = true
                scope.comments.forEach(function(comment) {
                    loadAvatar(comment).then(function(){})
                })
            }
        })

        scope.TimeService = TimeService
    }

    return directive
})