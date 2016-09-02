var omniService = angular.module("OmniWheel")

omniService.directive('voiceinput', function() {
    var directive = {};

    directive.restrict = 'E';

    directive.replace = true;

    directive.template = ''
                + '<md-card>'
                +       '<md-card-content layout="column">'
                +           '<div>{{info}}</div>'
                +           '<div id="results" layout="row">'
                +                   '<input ng-keypress="keyPress($event)" class="voice-input" type="text" ng-model="textTranscript.text" ng-if="textInput" flex="90"></input>'
                +                   '<div ng-hide="textInput" flex="90" layout="row" layout-align="start center">'
                +                       '<span class="final">{{finalTranscript}}</span> <span class="interim">{{interim}}</span>'
                +                   '</div>'
                +                   '<div layout="row" layout-align="center"><md-icon ng-click="sendClick()" md-svg-src="/images/send.svg"/></div>'
                +                   '<div><img ng-src="{{startButtonImage}}" ng-click="start($event)"/></div>'
                +           '</div>'
                +       '</md-card-content>'
                + '</md-card>'

    directive.scope = {
        finish: '&'
    };

    directive.link = function(scope, elem, attr){
        scope.startButtonImage = '/images/mic.gif'
        scope.infos = {
            'info_start': 'Click on the microphone icon and begin speaking.',

            'info_speak_now': 'Speak now.',

            'info_no_speech': 'No speech was detected. You may need to adjust your' +
                        + 'microphone settings.',

            'info_no_microphone': 'No microphone was found. Ensure that a microphone is installed and that'
                        + ' microphone settings are configured correctly.',

            'info_allow': 'Click the "Allow" button above to enable your microphone.',

            'info_denied': 'Permission to use microphone was denied.',

            'info_blocked': 'Permission to use microphone is blocked. To change,'
                        + 'go to chrome://settings/contentExceptions#media-stream',

            'info_upgrade': 'Web Speech API is not supported by this browser.'
                        + 'Upgrade to Chrome version 25 or later.',
            '':''
        }

        scope.info = ''

        scope.textInput = true

        scope.textTranscript = {
            "text": ""
        }

        scope.keyPress = function(e){
            if(e.keyCode == 13) {
                scope.sendClick()
            }
        }

        scope.sendClick = function() {
            scope.finish({'transcript':scope.textTranscript.text})
        }

        scope.safeApply = function(fn) {
            var phase = this.$root.$$phase;
            if(phase == '$apply' || phase == '$digest')
                this.$eval(fn);
            else
                this.$apply(fn);
        };

        function showInfo(s) {
            scope.safeApply(function() {
                scope.info = scope.infos[s]
            })
            console.log(scope.info)
        }

        scope.finalTranscript = ''
        var recognizing = false;
        var ignore_onend;
        var start_timestamp;

        if (!('webkitSpeechRecognition' in window)) {
            upgrade();
        } else {
            //start_button.style.display = 'inline-block';
            var recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;

            recognition.onstart = function() {
                recognizing = true;
                showInfo('info_speak_now');
                scope.startButtonImage = '/images/mic-animate.gif';
                scope.safeApply()
            };

            recognition.onerror = function(event) {
                if (event.error == 'no-speech') {
                    scope.startButtonImage = '/images/mic-slash.gif';
                    showInfo('info_no_speech');
                    ignore_onend = true;
                }
                if (event.error == 'audio-capture') {
                    scope.startButtonImage = '/images/mic-slash.gif';
                    showInfo('info_no_microphone');
                    ignore_onend = true;
                }
                if (event.error == 'not-allowed') {
                    if (event.timeStamp - start_timestamp < 100) {
                        showInfo('info_blocked');
                    } else {
                        showInfo('info_denied');
                    }
                    ignore_onend = true;
                }
                scope.textInput = true
            };

            recognition.onend = function() {
                recognizing = false;
                if (ignore_onend) {
                    return;
                }
                scope.startButtonImage = '/images/mic.gif';
                if (!scope.finalTranscript) {
                    showInfo('info_start');
                    return;
                }
                showInfo('');
            };

            recognition.onresult = function(event) {
                scope.safeApply(function() {
                    scope.interim = ''
                    for (var i = event.resultIndex; i < event.results.length; ++i) {
                        if (event.results[i].isFinal) {
                            scope.finalTranscript += event.results[i][0].transcript;
                            scope.finish({'transcript':scope.finalTranscript})
                            scope.textInput = true
                            scope.textTranscript.text = scope.finalTranscript
                        } else {
                            scope.interim += event.results[i][0].transcript
                        }
                    }
                })
            };
        }


        function upgrade() {
            scope.hideStart = true
            showInfo('info_upgrade');
        }

        scope.start = function(event) {
            if (recognizing) {
                recognition.stop();
                return;
            }
            scope.textInput = false
            scope.finalTranscript = '';
            scope.finalTranscript.text = ''
            recognition.lang = 'en-US';
            recognition.start();
            ignore_onend = false;
            scope.startButtonImage = '/images/mic.gif';
            showInfo('info_allow');
            start_timestamp = event.timeStamp;
        }
    }
    return directive
})