/*

	When starwars is migrated to big-thunder, delete this video.js,
	this code should not diverge from what is already in big-thunder,
	if this needs edited please keep them in sync.

*/

var TM = TM || {};

(function($){
	"use strict";

	TM.Utils = (function(utilsObj){

		utilsObj.hasDisneyEmbed = function (url) {
			// blah.com/embed but not blah.com/embed/module
			var re = /.*(disney\.(com|io)|starwars\.com).*\/embed\/(?!module\/)/g;
			return re.test(url);
		};

		// borrowed from Underscore.js 1.8.3
		utilsObj.throttle = function(func, wait, options) {
			var context, args, result;
			var timeout = null;
			var previous = 0;
			if (!options) {
				options = {};
			}
			var later = function() {
				previous = options.leading === false ? 0 : Date.now();
				timeout = null;
				result = func.apply(context, args);
				if (!timeout) {
					context = args = null;
				}
			};
			return function() {
				var now = Date.now();
				if (!previous && options.leading === false) {
					previous = now;
				}
				var remaining = wait - (now - previous);
				context = this;
				args = arguments;
				if (remaining <= 0 || remaining > wait) {
					if (timeout) {
						clearTimeout(timeout);
						timeout = null;
					}
					previous = now;
					result = func.apply(context, args);
					if (!timeout) {
						context = args = null;
					}
				} else if (!timeout && options.trailing !== false) {
					timeout = setTimeout(later, remaining);
				}
				return result;
			};
		};

		return utilsObj;
	}(TM.Utils || {}));


	function Evented(name) {
		this.name = name;
		this.callbacks = [];
	}
	Evented.prototype.registerCallback = function(callback) {
		this.callbacks.push(callback);
	};
	Evented.prototype.unRegisterCallback = function(callback) {
		var i = this.callbacks.indexOf(callback);
		if (i > -1) {
			this.callbacks.splice(i, 1);
		}
	};


	function Reactor() {
		this.events = {};
	}
	Reactor.prototype.registerEvent = function(eventName) {
		var event = new Evented(eventName);
		this.events[eventName] = event;
	};
	Reactor.prototype.dispatchEvent = function(eventName, eventArgs) {
		if (this.events[eventName]) {
			this.events[eventName].callbacks.forEach(function(cb) {
				cb(eventArgs);
			}, this);
		}
	};
	Reactor.prototype.addEventListener = function(eventName, callback) {
		// maaggiiiiic
		if (!this.events[eventName]) {
			this.registerEvent(eventName);
		}
		this.events[eventName].registerCallback(callback);
	};
	Reactor.prototype.removeEventListener = function(eventName, callback) {
		this.events[eventName].unRegisterCallback(callback);
	};


	// VideoState object to help compartmentalize functions and callbacks related to video state
	function VideoState(config) {
		this.defer = undefined; // will hold the Deferred object
		this.callCount = 0;
		this.eventBusCallbacks = [];

		this.name = config.name;
		this.onRun = config.onRun || function() {};
		this.onResolve = config.onResolve || function() {};
		this.resolveWhen = config.resolveWhen || [];
		this.requireStates = config.requireStates || [];
		this.maxCalls = config.maxCalls;
		this.eventBus = config.eventBus;

		this.resolveWhenEventCallback = function(data) {
			this.resolve(data[0]);
		}.bind(this);
	}

	// keep track of the event callbacks
	// we don't want the callbacks to last any longer than the lifetime of run()->resolve()
	VideoState.prototype.addEventListener = function(eventName, callback) {
		this.eventBusCallbacks.push({
			eventName: eventName,
			callback: callback
		});
		this.eventBus.addEventListener(eventName, callback);
	};

	VideoState.prototype.run = function() {
		this.callCount++;

		// starts with defer state of "pending"
		this.defer = $.Deferred();
		// when the defer is resolved, execute the onResolve function
		this.defer.promise().done(this.onResolve);

		// bind the event listeners
		this.resolveWhen.forEach(function(eventName) {
			this.addEventListener(eventName, this.resolveWhenEventCallback);
		}, this);

		this.onRun();

		return this.defer;
	};

	VideoState.prototype.resolve = function(eventName) {

		this.eventBusCallbacks.forEach(function(cbObj) {
			this.eventBus.removeEventListener(cbObj.eventName, cbObj.callback);
		}, this);
		this.eventBusCallbacks = [];

		if (this.defer.resolveWith) {
			this.defer.resolveWith(this, [eventName]);
		}
	};

	VideoState.prototype.state = function() {
		return (this.defer && this.defer.state) ? this.defer.state() : '';
	};



	function Video(el) {
		var video = this;

		this.el = el; // video iframe element
		this.id = this.getId();
		this.rect = {};
		this.stateQueue = []; // FIFO
		this.currentState = {};
		this.priorStates = []; // list of unique state names which have been called
		this.eventBus = new Reactor();
		this.eventBusCallbacks = [];
		this.muteSent = false;

		this.states = [
			new VideoState({
				name: 'load',
				resolveWhen: [
					'videoFinishedEmbedPoster', // desktop
					'videoMediaReady', // mobile width (maybe desktop)
					'videoFinishedEmbedPlayer' // iOS safari
				],
				maxCalls: 1,
				eventBus: this.eventBus
			}),
			new VideoState({
				name: 'play',
				onRun: function() {
					video.postMessage(['videoPlay']);
				},
				resolveWhen: ['videoPlayed'],
				requireStates: ['load'],
				eventBus: this.eventBus
			}),
			new VideoState({
				name: 'pause',
				onRun: function() {
					// sometimes if the pause is too close with play event, the player will not pause
					// sometimes it will play again after a pause without any postMessages being sent
					// TODO: when kalturaV3 is introduced, revisit this and see if the delay is still necessary
					setTimeout(function() {
						video.postMessage(['videoPause']);
					}, 250);
				},
				resolveWhen: ['videoPaused'],
				requireStates: ['play'],
				eventBus: this.eventBus
			}),
			new VideoState({
				name: 'complete',
				resolveWhen: ['videoPlayComplete'],
				requireStates: ['load', 'play'],
				maxCalls: 1,
				eventBus: this.eventBus
			})
		];

		this.setRect();

		// if the player sends the message at any time, align to that state
		this.forceTransitionWhen('videoPaused', 'pause');
		this.forceTransitionWhen('videoPlayed', 'play');

		// mediaReady is early enough to mute but not so early as to be ignored.
		// mute prior to playing, and only mute once!
		this.addEventListener('videoMediaReady', function() {
			this.muteOnce();
		}.bind(this));

		this.toState('load');
	}

	Video.prototype.getId = function() {
		var matches = this.el.src.match(/\/embed\/(\w+)/);
		if (matches && matches[1]) {
			return matches[1];
		}
	};

	Video.prototype.getOrigin = function() {
		var matches = this.el.src.match(/(https?:\/\/.*((diznee|disney|starwars|babble)\.(com|net|io)))\/embed\/.*/);
		if (matches && matches[1]) {
			return matches[1];
		}
	};

	Video.prototype.getRect = function() {
		// MDN says: Due to compatibility problems, it is safest to
		// rely on only properties left, top, right, and bottom.
		var rect = this.el.getBoundingClientRect();
		return {
			left: rect.left,
			top: rect.top,
			right: rect.right,
			bottom: rect.bottom
		};
	};

	Video.prototype.setRect = function() {
		this.rect = this.getRect();
	};

	// passing in a postMessage event
	Video.prototype.onMessage = function(data) {
		this.eventBus.dispatchEvent(data[0], data);
	};

	// keep track of the event callbacks
	// we don't want the callbacks to last any longer than the lifetime the Video
	Video.prototype.addEventListener = function(eventName, callback) {
		this.eventBusCallbacks.push({
			eventName: eventName,
			callback: callback
		});
		this.eventBus.addEventListener(eventName, callback);
	};

	// hang up the phone
	Video.prototype.removeEventListeners = function() {
		this.eventBusCallbacks.forEach(function(cbObj) {
			this.eventBus.removeEventListener(cbObj.eventName, cbObj.callback);
		}, this);
		this.eventBusCallbacks = [];
	};

	Video.prototype.getCurrentStateName = function() {
		return this.currentState.name || '';
	};

	Video.prototype.getCurrentStateStatus = function() {
		return this.currentState.state && this.currentState.state();
	};

	Video.prototype.toState = function(stateName) {
		var stateObj = this.getStateObj(stateName);

		if (stateObj && this.canQueueState(stateObj)) {
			this.stateQueue.push(stateName);
			this.runQueue();
		}
	};

	// sometimes we need to skip the line, if it exists,
	// and transition to a new state. such as
	// when the user interacts with the player UI
	Video.prototype.toStateImmediate = function(stateName) {
		var stateObj = this.getStateObj(stateName);

		// any event with a forceTransitionWhen listener and a
		// similar one at the state object will hit our function
		if (this.getCurrentStateName() === stateName) {
			return;
		}

		if (stateObj) {

			// resolve the current state if need be
			if (this.currentState.state() === 'pending') {
				this.currentState.resolve();
			}

			// set currentState to stateName state
			// we don't execute any functions on the state object since this transitions is
			// after-the-fact, ex: someone is muting or playing the player.
			// other code locations may compare against the current state,
			// keep our state in sync with the player
			this.currentState = stateObj;
		}
	};

	Video.prototype.getStateObj = function(stateName) {
		var states = this.states.filter(function(stateObj) {
			return stateObj.name === stateName;
		});
		return states.length ? states[0] : false;
	};

	Video.prototype.postMessage = function(args) {
		this.el.contentWindow.postMessage(args, '*');
	};

	Video.prototype.canQueueState = function(stateObj) {

		// deny if current state
		if (this.getCurrentStateName() === stateObj.name) {
			return false;
		}

		// deny if any prior state requirement has not yet executed
		if (stateObj.requireStates.length) {
			var needsPriorState = stateObj.requireStates.some(function(reqStateName) {
				return this.priorStates.indexOf(reqStateName) === -1;
			}, this);

			if (needsPriorState) {
				return false;
			}
		}

		// deny if already queued
		if (this.stateQueue.indexOf(stateObj.name) > -1) {
			return false;
		}

		// deny if maxCalls reached
		if (stateObj.maxCalls && stateObj.callCount >= stateObj.maxCalls) {
			return false;
		}

		return true;
	};

	Video.prototype.runQueue = function() {

		// skip if a state is in progress since it will execute runQueue when the state resolves
		if (this.getCurrentStateStatus() !== 'pending' && this.stateQueue.length) {

			var stateObj = this.getStateObj(this.stateQueue.shift());

			if (stateObj) {
				this.currentState = stateObj;

				this.logPriorState(this.currentState.name);

				this.currentState.run();

				this.currentState.defer.promise().done(function() {
					// on to the next state, should there be one queued up
					this.runQueue();
				}.bind(this));
			}
		}
	};

	// bind an eventName to a specific video state
	Video.prototype.forceTransitionWhen = function(eventName, stateName) {
		var self = this;
		var callback = function(data) {
			self.toStateImmediate(stateName);
		};

		this.addEventListener(eventName, callback);
	};

	Video.prototype.logPriorState = function(stateName) {
		if (this.priorStates.indexOf(stateName) === -1) {
			this.priorStates.push(stateName);
		}
	};

	Video.prototype.muteOnce = function() {
		if (!this.muteSent) {
			this.postMessage(['videoMute', true]);
			this.muteSent = true;
		}
	};



	TM.AutoPlayController = (function(apc) {
		var videos = [],
			visibleVideos = [];

		apc.origins = [];

		// threshold is float for percentage of visibile: .4 = 40% visible
		var inView = function(rect, threshold) {
			var top = rect.top,
				bottom = rect.bottom,
				width = rect.right - rect.left,
				height = rect.bottom - rect.top,
				surfaceArea = width * height,
				winTop = window.pageYOffset,
				winBottom = winTop + window.innerHeight,
				viewPortHeight = winBottom - winTop;

			threshold = parseFloat(threshold);
			threshold = !isNaN(threshold) ? threshold : 1;

			// top and bottom are within the viewport
			if (top >= 0 && bottom <= viewPortHeight) {
				return true;
			// not fully visible
			} else if (threshold === 1) {
				return false;
			// partial visibility via threshold
			} else if (threshold > 0 && threshold < 1) {
				var visibleSurfaceArea = 0,
					visibleRatio = 0;
				// below viewport
				if (bottom > viewPortHeight) {
					visibleSurfaceArea = (viewPortHeight - top) * width;
					visibleRatio = visibleSurfaceArea / surfaceArea;
					return visibleRatio > threshold;
				// above viewport
				} else if (top < 0) {
					visibleSurfaceArea = bottom * width;
					visibleRatio = visibleSurfaceArea / surfaceArea;
					return visibleRatio > threshold;
				// not sure how we got here
				} else {
					return false;
				}
			} else {
				return false;
			}
		};

		apc.requestToState = function(stateName, video) {
			if (video.getCurrentStateName() !== stateName) {
				video.toState(stateName);
			}
		};

		// a new video has been added to the page, yay
		apc.addVideo = function(el) {
			// early out on iOS
			// TODO: remove for kalturaV3
			if (!!navigator.platform && /iPad|iPhone|iPod/.test(navigator.platform)) {
				return;
			}
			// same, remove for kalturaV3
			// some android devices will not play the first video
			if (/android/i.test(navigator.userAgent)) {
				return;
			}

			var vid = new Video(el);
			videos.push(vid);
			apc.addOrigin(vid.getOrigin());
		};

		apc.addOrigin = function (origin) {
			if (apc.origins.indexOf(origin) === -1) {
				apc.origins.push(origin);
			}
		};

		// good luck out there
		apc.nukeVideoFromOrbit = function(v) {

			v.removeEventListeners();

			var i = -1;
			// video object source of truth
			i = videos.indexOf(v);
			if (i > -1) {
				videos.splice(i, 1);
			}
			// from the visible video source of truth
			i = visibleVideos.indexOf(v);
			if (i > -1) {
				visibleVideos.splice(i, 1);
			}
		};

		apc.playComplete = function(v) {
			apc.nukeVideoFromOrbit(v);
			apc.playFirstVisibleAvailable();
		};

		// pass postMessage to the video object
		apc.onMessage = function(data) {

			// second element of the postMessage array should be the videoId
			if (data && data[1]) {
				videos.forEach(function(v) {
					if (v.id === data[1]) {
						// ids match, pass the message
						v.onMessage(data);

						if (data[0] === 'videoPlayComplete') {
							apc.playComplete(v);
						}
					}
				});
			}
		};

		// play visible video if none already playing
		apc.playFirstVisibleAvailable = function() {

			// early out if a visible video is in the play state
			var playingVids = visibleVideos.some(function(v) {
				return v.getCurrentStateName() === 'play';
			}, this);

			if (playingVids) {
				return;
			}

			// visible videos in a state that can be transitioned to play
			var readyVids = visibleVideos.filter(function(v) {
				// vid state is one of
				return ['load', 'pause'].indexOf(v.getCurrentStateName()) > -1;
			});

			if (readyVids.length) {
				apc.requestToState('play', readyVids[0]);
			}
		};

		apc.scroll = function() {
			if (videos.length) {
				videos.forEach(function(v) {
					var i = -1;

					// update the video rectangle
					v.setRect();

					// still loading? don't request any state changes
					if (v.getCurrentStateName() === 'load' && v.getCurrentStateStatus() === 'pending') {
						// noop
					// if within viewport, request play
					} else if (inView(v.rect, 0.5)) {

						// video coming into view
						i = visibleVideos.indexOf(v);
						if (i === -1) {
							visibleVideos.push(v);
							apc.playFirstVisibleAvailable();
						}

					// if not within viewport, request pause
					} else {
						// video went out of view
						i = visibleVideos.indexOf(v);
						if (i > -1) {
							visibleVideos.splice(i, 1);

							apc.requestToState('pause', v);
							apc.playFirstVisibleAvailable();
						}
					}
				});
			}

		};

		// Be careful with the interval, setting it too low will have negative performance implications
		$(window).on('scroll touchmove', TM.Utils.throttle(apc.scroll, 200));

		document.body.addEventListener('TMInfiniteGetNextPost', function(result) {
			result.detail.nextPost.find('iframe').each(function(i, el) {
				if (TM.Utils.hasDisneyEmbed(el.src)) {
					apc.addVideo(el);
				}
			});
		});

		// Look for embeds on page load
		$('body iframe').each(function(i, el) {
			if (TM.Utils.hasDisneyEmbed(el.src)) {
				apc.addVideo(el);
			}
		});

		// postMessage events from the video players (and many other things!)
		window.addEventListener('message', function(event) {
			if (apc.origins.indexOf(event.origin) > -1) {
				apc.onMessage(event.data);
			}
		});

		return apc;
	}(TM.AutoPlayController || {}));
}(jQuery));
