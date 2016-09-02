var omniService = angular.module("OmniWheel")

omniService.directive('omniJira', function(TimeService) {
    var directive = {};

    directive.restrict = 'E';

    directive.replace = true;

    directive.template = ''
                + '<div layout="row">'
                +       '<div flex="100" ng-if="initialised">'
                +           '<h3>{{jira.key}} : {{jira.fields.summary}}</h3>'
                +           '<div layout="column">'
                +               '<div layout="row">'
                +                   '<div flex="30"><p class="omni_jira_line"><strong>Type:</strong></p></div>'
                +                   '<div flex="70"><p class="omni_jira_line">{{issuetype.name}}</p></div>'
                +               '</div>'
                +               '<div layout="row">'
                +                   '<div flex="30"><p class="omni_jira_line"><strong>Status:</strong></p></div>'
                +                   '<div flex="70"><p class="omni_jira_line">{{status.name}}</p></div>'
                +               '</div>'
                +               '<div layout="row">'
                +                   '<div flex="30"><p class="omni_jira_line"><strong>Priority:</strong></p></div>'
                +                   '<div flex="70"><p class="omni_jira_line">{{priority.name}}</p></div>'
                +               '</div>'
                +               '<div layout="row">'
                +                   '<div flex="30"><p class="omni_jira_line"><strong>Assignee:</strong></p></div>'
                +                   '<div flex="70"><p class="omni_jira_line">{{assignee.displayName}}</p></div>'
                +               '</div>'
                +               '<div layout="row">'
                +                   '<div flex="30"><p class="omni_jira_line"><strong>Reporter:</strong></p></div>'
                +                   '<div flex="70"><p class="omni_jira_line">{{reporter.displayName}}</p></div>'
                +               '</div>'
                +               '<div layout="row">'
                +                   '<div flex="30"><p class="omni_jira_line"><strong>Version:</strong></p></div>'
                +                   '<div flex="70"><p class="omni_jira_line"><span style="background: #E5E5E5; padding:2px;" ng-repeat="v in versions">{{v.name}}</span></p></div>'
                +               '</div>'
                +               '<div layout="row">'
                +                   '<div flex="30"><p class="omni_jira_line"><strong>Components:</strong></p></div>'
                +                   '<div flex="70"><p class="omni_jira_line"><span style="background: #E5E5E5; padding:2px;" ng-repeat="c in components">{{c.name}}</span></p></div>'
                +               '</div>'
                +               '<div layout="row">'
                +                   '<div flex="30"><p class="omni_jira_line"><strong>Labels:</strong></p></div>'
                +                   '<div flex="70"><p class="omni_jira_line"><span style="background: #E5E5E5; padding:2px;" ng-repeat="l in labels">{{l.name}}</span></p></div>'
                +               '</div>'
                +               '<div layout="row">'
                +                   '<div flex="30"><p class="omni_jira_line"><strong>Fix Versions:</strong></p></div>'
                +                   '<div flex="70"><p class="omni_jira_line"><span style="background: #E5E5E5; padding:2px;" ng-repeat="f in fixVersions">{{f.name}}</span></p></div>'
                +               '</div>'
                +               '<div layout="row">'
                +                   '<div flex="30"><p class="omni_jira_line"><strong>Created:</strong></p></div>'
                +                   '<div flex="70"><p class="omni_jira_line">{{TimeService.formatTime(jira.fields.created)}}</p></div>'
                +               '</div>'
                +               '<div layout="row">'
                +                   '<div flex="30"><p class="omni_jira_line"><strong>Updated:</strong></p></div>'
                +                   '<div flex="70"><p class="omni_jira_line">{{TimeService.formatTime(jira.fields.updated)}}</p></div>'
                +               '</div>'
                +           '</div>'
                +           '<p><strong>Description</strong></p>'
                +           '<p>{{jira.fields.description}}</p>'
                +       '</div>'
                + '</div>'

    directive.scope = {
            jira: '='
    };

    directive.link = function(scope, elem, attr){
        scope.initialised = false
        scope.issuetype = {}
        scope.reporter = {}
        scope.assignee = {}
        scope.status = {}
        scope.priority = {}

        scope.versions = []
        scope.components = []
        scope.labels = []
        scope.fixVersions = []

        scope.$watch(function() {
            return scope.jira
        }, function(n,o) {
            if(scope.jira != undefined && scope.jira != null && scope.jira != {}) {
                scope.initialised = true
                scope.issuetype = scope.jira.fields.issuetype
                scope.reporter = scope.jira.fields.reporter
                scope.assignee = scope.jira.fields.assignee
                scope.status = scope.jira.fields.status
                scope.priority = scope.jira.fields.priority
                scope.versions = scope.jira.fields.versions
                scope.components = scope.jira.fields.components
                scope.labels = scope.jira.fields.labels
                scope.fixVersions = scope.jira.fields.fixVersions
            }
        })

        scope.TimeService = TimeService
    }
    return directive
})