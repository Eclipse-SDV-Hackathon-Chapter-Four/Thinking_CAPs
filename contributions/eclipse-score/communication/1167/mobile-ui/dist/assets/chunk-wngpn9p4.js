import{da as W6,ea as d7}from"./chunk-zrxh0jsv.js";var J6=d7((JX,G7)=>{(function(){function X($,L){Object.defineProperty(Y.prototype,$,{get:function(){console.warn("%s(...) is deprecated in plain JavaScript React classes. %s",L[0],L[1])}})}function Q($){if($===null||typeof $!=="object")return null;return $=L5&&$[L5]||$["@@iterator"],typeof $==="function"?$:null}function Z($,L){$=($=$.constructor)&&($.displayName||$.name)||"ReactClass";var E=$+"."+L;Q5[E]||(console.error("Can't call %s on a component that is not yet mounted. This is a no-op, but it might indicate a bug in your application. Instead, assign to `this.state` directly or define a `state = {};` class property with the desired state in the %s component.",L,$),Q5[E]=!0)}function Y($,L,E){this.props=$,this.context=L,this.refs=W5,this.updater=E||P5}function J(){}function W($,L,E){this.props=$,this.context=L,this.refs=W5,this.updater=E||P5}function G(){}function q($){return""+$}function U($){try{q($);var L=!1}catch(m){L=!0}if(L){L=console;var E=L.error,N=typeof Symbol==="function"&&Symbol.toStringTag&&$[Symbol.toStringTag]||$.constructor.name||"Object";return E.call(L,"The provided key is an unsupported type %s. This value must be coerced to a string before using it here.",N),q($)}}function A($){if($==null)return null;if(typeof $==="function")return $.$$typeof===g7?null:$.displayName||$.name||null;if(typeof $==="string")return $;switch($){case N4:return"Fragment";case T:return"Profiler";case H:return"StrictMode";case D4:return"Suspense";case c:return"SuspenseList";case b4:return"Activity"}if(typeof $==="object")switch(typeof $.tag==="number"&&console.error("Received an unexpected object in getComponentNameFromType(). This is likely a bug in React. Please file an issue."),$.$$typeof){case $4:return"Portal";case p:return $.displayName||"Context";case x:return($._context.displayName||"Context")+".Consumer";case j4:var L=$.render;return $=$.displayName,$||($=L.displayName||L.name||"",$=$!==""?"ForwardRef("+$+")":"ForwardRef"),$;case Z4:return L=$.displayName||null,L!==null?L:A($.type)||"Memo";case T4:L=$._payload,$=$._init;try{return A($(L))}catch(E){}}return null}function M($){if($===N4)return"<>";if(typeof $==="object"&&$!==null&&$.$$typeof===T4)return"<...>";try{var L=A($);return L?"<"+L+">":"<...>"}catch(E){return"<...>"}}function O(){var $=r.A;return $===null?null:$.getOwner()}function z(){return Error("react-stack-top-frame")}function j($){if(t4.call($,"key")){var L=Object.getOwnPropertyDescriptor($,"key").get;if(L&&L.isReactWarning)return!1}return $.key!==void 0}function B($,L){function E(){r6||(r6=!0,console.error("%s: `key` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://react.dev/link/special-props)",L))}E.isReactWarning=!0,Object.defineProperty($,"key",{get:E,configurable:!0})}function R(){var $=A(this.type);return a5[$]||(a5[$]=!0,console.error("Accessing element.ref was removed in React 19. ref is now a regular prop. It will be removed from the JSX Element type in a future release.")),$=this.props.ref,$!==void 0?$:null}function D($,L,E,N,m,a){var s=E.ref;return $={$$typeof:B4,type:$,key:L,props:E,_owner:N},(s!==void 0?s:null)!==null?Object.defineProperty($,"ref",{enumerable:!1,get:R}):Object.defineProperty($,"ref",{enumerable:!1,value:null}),$._store={},Object.defineProperty($._store,"validated",{configurable:!1,enumerable:!1,writable:!0,value:0}),Object.defineProperty($,"_debugInfo",{configurable:!1,enumerable:!1,writable:!0,value:null}),Object.defineProperty($,"_debugStack",{configurable:!1,enumerable:!1,writable:!0,value:m}),Object.defineProperty($,"_debugTask",{configurable:!1,enumerable:!1,writable:!0,value:a}),Object.freeze&&(Object.freeze($.props),Object.freeze($)),$}function b($,L){return L=D($.type,L,$.props,$._owner,$._debugStack,$._debugTask),$._store&&(L._store.validated=$._store.validated),L}function w($){F($)?$._store&&($._store.validated=1):typeof $==="object"&&$!==null&&$.$$typeof===T4&&($._payload.status==="fulfilled"?F($._payload.value)&&$._payload.value._store&&($._payload.value._store.validated=1):$._store&&($._store.validated=1))}function F($){return typeof $==="object"&&$!==null&&$.$$typeof===B4}function V($){var L={"=":"=0",":":"=2"};return"$"+$.replace(/[=:]/g,function(E){return L[E]})}function k($,L){return typeof $==="object"&&$!==null&&$.key!=null?(U($.key),V(""+$.key)):L.toString(36)}function P($){switch($.status){case"fulfilled":return $.value;case"rejected":throw $.reason;default:switch(typeof $.status==="string"?$.then(G,G):($.status="pending",$.then(function(L){$.status==="pending"&&($.status="fulfilled",$.value=L)},function(L){$.status==="pending"&&($.status="rejected",$.reason=L)})),$.status){case"fulfilled":return $.value;case"rejected":throw $.reason}}throw $}function h($,L,E,N,m){var a=typeof $;if(a==="undefined"||a==="boolean")$=null;var s=!1;if($===null)s=!0;else switch(a){case"bigint":case"string":case"number":s=!0;break;case"object":switch($.$$typeof){case B4:case $4:s=!0;break;case T4:return s=$._init,h(s($._payload),L,E,N,m)}}if(s){s=$,m=m(s);var i=N===""?"."+k(s,0):N;return r5(m)?(E="",i!=null&&(E=i.replace(B5,"$&/")+"/"),h(m,L,E,"",function(m4){return m4})):m!=null&&(F(m)&&(m.key!=null&&(s&&s.key===m.key||U(m.key)),E=b(m,E+(m.key==null||s&&s.key===m.key?"":(""+m.key).replace(B5,"$&/")+"/")+i),N!==""&&s!=null&&F(s)&&s.key==null&&s._store&&!s._store.validated&&(E._store.validated=2),m=E),L.push(m)),1}if(s=0,i=N===""?".":N+":",r5($))for(var l=0;l<$.length;l++)N=$[l],a=i+k(N,l),s+=h(N,L,E,a,m);else if(l=Q($),typeof l==="function")for(l===$.entries&&(O5||console.warn("Using Maps as children is not supported. Use an array of keyed ReactElements instead."),O5=!0),$=l.call($),l=0;!(N=$.next()).done;)N=N.value,a=i+k(N,l++),s+=h(N,L,E,a,m);else if(a==="object"){if(typeof $.then==="function")return h(P($),L,E,N,m);throw L=String($),Error("Objects are not valid as a React child (found: "+(L==="[object Object]"?"object with keys {"+Object.keys($).join(", ")+"}":L)+"). If you meant to render a collection of children, use an array instead.")}return s}function G4($,L,E){if($==null)return $;var N=[],m=0;return h($,N,"","",function(a){return L.call(E,a,m++)}),N}function z4($){if($._status===-1){var L=$._ioInfo;L!=null&&(L.start=L.end=performance.now()),L=$._result;var E=L();if(E.then(function(m){if($._status===0||$._status===-1){$._status=1,$._result=m;var a=$._ioInfo;a!=null&&(a.end=performance.now()),E.status===void 0&&(E.status="fulfilled",E.value=m)}},function(m){if($._status===0||$._status===-1){$._status=2,$._result=m;var a=$._ioInfo;a!=null&&(a.end=performance.now()),E.status===void 0&&(E.status="rejected",E.reason=m)}}),L=$._ioInfo,L!=null){L.value=E;var N=E.displayName;typeof N==="string"&&(L.name=N)}$._status===-1&&($._status=0,$._result=E)}if($._status===1)return L=$._result,L===void 0&&console.error(`lazy: Expected the result of a dynamic import() call. Instead received: %s

Your code should look like: 
  const MyComponent = lazy(() => import('./MyComponent'))

Did you accidentally put curly braces around the import?`,L),"default"in L||console.error(`lazy: Expected the result of a dynamic import() call. Instead received: %s

Your code should look like: 
  const MyComponent = lazy(() => import('./MyComponent'))`,L),L.default;throw $._result}function d(){var $=r.H;return $===null&&console.error(`Invalid hook call. Hooks can only be called inside of the body of a function component. This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://react.dev/link/invalid-hook-call for tips about how to debug and fix this problem.`),$}function Y4(){r.asyncTransitions--}function q4($){if(U5===null)try{var L=("require"+Math.random()).slice(0,7);U5=(G7&&G7[L]).call(G7,"timers").setImmediate}catch(E){U5=function(N){F6===!1&&(F6=!0,typeof MessageChannel>"u"&&console.error("This browser does not have a MessageChannel implementation, so enqueuing tasks via await act(async () => ...) will fail. Please file an issue at https://github.com/facebook/react/issues if you encounter this warning."));var m=new MessageChannel;m.port1.onmessage=N,m.port2.postMessage(void 0)}}return U5($)}function t($){return 1<$.length&&typeof AggregateError==="function"?AggregateError($):$[0]}function e($,L){L!==t5-1&&console.error("You seem to have overlapping act() calls, this is not supported. Be sure to await previous act() calls before making a new one. "),t5=L}function E4($,L,E){var N=r.actQueue;if(N!==null)if(N.length!==0)try{W4(N),q4(function(){return E4($,L,E)});return}catch(m){r.thrownErrors.push(m)}else r.actQueue=null;0<r.thrownErrors.length?(N=t(r.thrownErrors),r.thrownErrors.length=0,E(N)):L($)}function W4($){if(!V6){V6=!0;var L=0;try{for(;L<$.length;L++){var E=$[L];do{r.didUsePromise=!1;var N=E(!1);if(N!==null){if(r.didUsePromise){$[L]=E,$.splice(0,L);return}E=N}else break}while(1)}$.length=0}catch(m){$.splice(0,L+1),r.thrownErrors.push(m)}finally{V6=!1}}}typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"&&typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart==="function"&&__REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStart(Error());var B4=Symbol.for("react.transitional.element"),$4=Symbol.for("react.portal"),N4=Symbol.for("react.fragment"),H=Symbol.for("react.strict_mode"),T=Symbol.for("react.profiler"),x=Symbol.for("react.consumer"),p=Symbol.for("react.context"),j4=Symbol.for("react.forward_ref"),D4=Symbol.for("react.suspense"),c=Symbol.for("react.suspense_list"),Z4=Symbol.for("react.memo"),T4=Symbol.for("react.lazy"),b4=Symbol.for("react.activity"),L5=Symbol.iterator,Q5={},P5={isMounted:function(){return!1},enqueueForceUpdate:function($){Z($,"forceUpdate")},enqueueReplaceState:function($){Z($,"replaceState")},enqueueSetState:function($){Z($,"setState")}},c4=Object.assign,W5={};Object.freeze(W5),Y.prototype.isReactComponent={},Y.prototype.setState=function($,L){if(typeof $!=="object"&&typeof $!=="function"&&$!=null)throw Error("takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,$,L,"setState")},Y.prototype.forceUpdate=function($){this.updater.enqueueForceUpdate(this,$,"forceUpdate")};var X4={isMounted:["isMounted","Instead, make sure to clean up subscriptions and pending requests in componentWillUnmount to prevent memory leaks."],replaceState:["replaceState","Refactor your code to use setState instead (see https://github.com/facebook/react/issues/3236)."]};for(y5 in X4)X4.hasOwnProperty(y5)&&X(y5,X4[y5]);J.prototype=Y.prototype,X4=W.prototype=new J,X4.constructor=W,c4(X4,Y.prototype),X4.isPureReactComponent=!0;var r5=Array.isArray,g7=Symbol.for("react.client.reference"),r={H:null,A:null,T:null,S:null,actQueue:null,asyncTransitions:0,isBatchingLegacy:!1,didScheduleLegacyUpdate:!1,didUsePromise:!1,thrownErrors:[],getCurrentStack:null,recentlyCreatedOwnerStacks:0},t4=Object.prototype.hasOwnProperty,o6=console.createTask?console.createTask:function(){return null};X4={react_stack_bottom_frame:function($){return $()}};var r6,K4,a5={},f5=X4.react_stack_bottom_frame.bind(X4,z)(),n5=o6(M(z)),O5=!1,B5=/\/+/g,j5=typeof reportError==="function"?reportError:function($){if(typeof window==="object"&&typeof window.ErrorEvent==="function"){var L=new window.ErrorEvent("error",{bubbles:!0,cancelable:!0,message:typeof $==="object"&&$!==null&&typeof $.message==="string"?String($.message):String($),error:$});if(!window.dispatchEvent(L))return}else if(typeof process==="object"&&typeof process.emit==="function"){process.emit("uncaughtException",$);return}console.error($)},F6=!1,U5=null,t5=0,_5=!1,V6=!1,R6=typeof queueMicrotask==="function"?function($){queueMicrotask(function(){return queueMicrotask($)})}:q4;X4=Object.freeze({__proto__:null,c:function($){return d().useMemoCache($)}});var y5={map:G4,forEach:function($,L,E){G4($,function(){L.apply(this,arguments)},E)},count:function($){var L=0;return G4($,function(){L++}),L},toArray:function($){return G4($,function(L){return L})||[]},only:function($){if(!F($))throw Error("React.Children.only expected to receive a single React element child.");return $}};JX.Activity=b4,JX.Children=y5,JX.Component=Y,JX.Fragment=N4,JX.Profiler=T,JX.PureComponent=W,JX.StrictMode=H,JX.Suspense=D4,JX.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=r,JX.__COMPILER_RUNTIME=X4,JX.act=function($){var L=r.actQueue,E=t5;t5++;var N=r.actQueue=L!==null?L:[],m=!1;try{var a=$()}catch(l){r.thrownErrors.push(l)}if(0<r.thrownErrors.length)throw e(L,E),$=t(r.thrownErrors),r.thrownErrors.length=0,$;if(a!==null&&typeof a==="object"&&typeof a.then==="function"){var s=a;return R6(function(){m||_5||(_5=!0,console.error("You called act(async () => ...) without await. This could lead to unexpected testing behaviour, interleaving multiple act calls and mixing their scopes. You should - await act(async () => ...);"))}),{then:function(l,m4){m=!0,s.then(function(z5){if(e(L,E),E===0){try{W4(N),q4(function(){return E4(z5,l,m4)})}catch(m7){r.thrownErrors.push(m7)}if(0<r.thrownErrors.length){var I7=t(r.thrownErrors);r.thrownErrors.length=0,m4(I7)}}else l(z5)},function(z5){e(L,E),0<r.thrownErrors.length?(z5=t(r.thrownErrors),r.thrownErrors.length=0,m4(z5)):m4(z5)})}}}var i=a;if(e(L,E),E===0&&(W4(N),N.length!==0&&R6(function(){m||_5||(_5=!0,console.error("A component suspended inside an `act` scope, but the `act` call was not awaited. When testing React components that depend on asynchronous data, you must await the result:\n\nawait act(() => ...)"))}),r.actQueue=null),0<r.thrownErrors.length)throw $=t(r.thrownErrors),r.thrownErrors.length=0,$;return{then:function(l,m4){m=!0,E===0?(r.actQueue=N,q4(function(){return E4(i,l,m4)})):l(i)}}},JX.cache=function($){return function(){return $.apply(null,arguments)}},JX.cacheSignal=function(){return null},JX.captureOwnerStack=function(){var $=r.getCurrentStack;return $===null?null:$()},JX.cloneElement=function($,L,E){if($===null||$===void 0)throw Error("The argument must be a React element, but you passed "+$+".");var N=c4({},$.props),m=$.key,a=$._owner;if(L!=null){var s;X:{if(t4.call(L,"ref")&&(s=Object.getOwnPropertyDescriptor(L,"ref").get)&&s.isReactWarning){s=!1;break X}s=L.ref!==void 0}s&&(a=O()),j(L)&&(U(L.key),m=""+L.key);for(i in L)!t4.call(L,i)||i==="key"||i==="__self"||i==="__source"||i==="ref"&&L.ref===void 0||(N[i]=L[i])}var i=arguments.length-2;if(i===1)N.children=E;else if(1<i){s=Array(i);for(var l=0;l<i;l++)s[l]=arguments[l+2];N.children=s}N=D($.type,m,N,a,$._debugStack,$._debugTask);for(m=2;m<arguments.length;m++)w(arguments[m]);return N},JX.createContext=function($){return $={$$typeof:p,_currentValue:$,_currentValue2:$,_threadCount:0,Provider:null,Consumer:null},$.Provider=$,$.Consumer={$$typeof:x,_context:$},$._currentRenderer=null,$._currentRenderer2=null,$},JX.createElement=function($,L,E){for(var N=2;N<arguments.length;N++)w(arguments[N]);N={};var m=null;if(L!=null)for(l in K4||!("__self"in L)||"key"in L||(K4=!0,console.warn("Your app (or one of its dependencies) is using an outdated JSX transform. Update to the modern JSX transform for faster performance: https://react.dev/link/new-jsx-transform")),j(L)&&(U(L.key),m=""+L.key),L)t4.call(L,l)&&l!=="key"&&l!=="__self"&&l!=="__source"&&(N[l]=L[l]);var a=arguments.length-2;if(a===1)N.children=E;else if(1<a){for(var s=Array(a),i=0;i<a;i++)s[i]=arguments[i+2];Object.freeze&&Object.freeze(s),N.children=s}if($&&$.defaultProps)for(l in a=$.defaultProps,a)N[l]===void 0&&(N[l]=a[l]);m&&B(N,typeof $==="function"?$.displayName||$.name||"Unknown":$);var l=1e4>r.recentlyCreatedOwnerStacks++;return D($,m,N,O(),l?Error("react-stack-top-frame"):f5,l?o6(M($)):n5)},JX.createRef=function(){var $={current:null};return Object.seal($),$},JX.forwardRef=function($){$!=null&&$.$$typeof===Z4?console.error("forwardRef requires a render function but received a `memo` component. Instead of forwardRef(memo(...)), use memo(forwardRef(...))."):typeof $!=="function"?console.error("forwardRef requires a render function but was given %s.",$===null?"null":typeof $):$.length!==0&&$.length!==2&&console.error("forwardRef render functions accept exactly two parameters: props and ref. %s",$.length===1?"Did you forget to use the ref parameter?":"Any additional parameter will be undefined."),$!=null&&$.defaultProps!=null&&console.error("forwardRef render functions do not support defaultProps. Did you accidentally pass a React component?");var L={$$typeof:j4,render:$},E;return Object.defineProperty(L,"displayName",{enumerable:!1,configurable:!0,get:function(){return E},set:function(N){E=N,$.name||$.displayName||(Object.defineProperty($,"name",{value:N}),$.displayName=N)}}),L},JX.isValidElement=F,JX.lazy=function($){$={_status:-1,_result:$};var L={$$typeof:T4,_payload:$,_init:z4},E={name:"lazy",start:-1,end:-1,value:null,owner:null,debugStack:Error("react-stack-top-frame"),debugTask:console.createTask?console.createTask("lazy()"):null};return $._ioInfo=E,L._debugInfo=[{awaited:E}],L},JX.memo=function($,L){$==null&&console.error("memo: The first argument must be a component. Instead received: %s",$===null?"null":typeof $),L={$$typeof:Z4,type:$,compare:L===void 0?null:L};var E;return Object.defineProperty(L,"displayName",{enumerable:!1,configurable:!0,get:function(){return E},set:function(N){E=N,$.name||$.displayName||(Object.defineProperty($,"name",{value:N}),$.displayName=N)}}),L},JX.startTransition=function($){var L=r.T,E={};E._updatedFibers=new Set,r.T=E;try{var N=$(),m=r.S;m!==null&&m(E,N),typeof N==="object"&&N!==null&&typeof N.then==="function"&&(r.asyncTransitions++,N.then(Y4,Y4),N.then(G,j5))}catch(a){j5(a)}finally{L===null&&E._updatedFibers&&($=E._updatedFibers.size,E._updatedFibers.clear(),10<$&&console.warn("Detected a large number of updates inside startTransition. If this is due to a subscription please re-write it to use React provided hooks. Otherwise concurrent mode guarantees are off the table.")),L!==null&&E.types!==null&&(L.types!==null&&L.types!==E.types&&console.error("We expected inner Transitions to have transferred the outer types set and that you cannot add to the outer Transition while inside the inner.This is a bug in React."),L.types=E.types),r.T=L}},JX.unstable_useCacheRefresh=function(){return d().useCacheRefresh()},JX.use=function($){return d().use($)},JX.useActionState=function($,L,E){return d().useActionState($,L,E)},JX.useCallback=function($,L){return d().useCallback($,L)},JX.useContext=function($){var L=d();return $.$$typeof===x&&console.error("Calling useContext(Context.Consumer) is not supported and will cause bugs. Did you mean to call useContext(Context) instead?"),L.useContext($)},JX.useDebugValue=function($,L){return d().useDebugValue($,L)},JX.useDeferredValue=function($,L){return d().useDeferredValue($,L)},JX.useEffect=function($,L){return $==null&&console.warn("React Hook useEffect requires an effect callback. Did you forget to pass a callback to the hook?"),d().useEffect($,L)},JX.useEffectEvent=function($){return d().useEffectEvent($)},JX.useId=function(){return d().useId()},JX.useImperativeHandle=function($,L,E){return d().useImperativeHandle($,L,E)},JX.useInsertionEffect=function($,L){return $==null&&console.warn("React Hook useInsertionEffect requires an effect callback. Did you forget to pass a callback to the hook?"),d().useInsertionEffect($,L)},JX.useLayoutEffect=function($,L){return $==null&&console.warn("React Hook useLayoutEffect requires an effect callback. Did you forget to pass a callback to the hook?"),d().useLayoutEffect($,L)},JX.useMemo=function($,L){return d().useMemo($,L)},JX.useOptimistic=function($,L){return d().useOptimistic($,L)},JX.useReducer=function($,L,E){return d().useReducer($,L,E)},JX.useRef=function($){return d().useRef($)},JX.useState=function($){return d().useState($)},JX.useSyncExternalStore=function($,L,E){return d().useSyncExternalStore($,L,E)},JX.useTransition=function(){return d().useTransition()},JX.version="19.2.4",typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<"u"&&typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop==="function"&&__REACT_DEVTOOLS_GLOBAL_HOOK__.registerInternalModuleStop(Error())})()});var GX=d7((WX)=>{var I5=W6(J6());(function(){function X(H){if(H==null)return null;if(typeof H==="function")return H.$$typeof===d?null:H.displayName||H.name||null;if(typeof H==="string")return H;switch(H){case R:return"Fragment";case b:return"Profiler";case D:return"StrictMode";case k:return"Suspense";case P:return"SuspenseList";case z4:return"Activity"}if(typeof H==="object")switch(typeof H.tag==="number"&&console.error("Received an unexpected object in getComponentNameFromType(). This is likely a bug in React. Please file an issue."),H.$$typeof){case B:return"Portal";case F:return H.displayName||"Context";case w:return(H._context.displayName||"Context")+".Consumer";case V:var T=H.render;return H=H.displayName,H||(H=T.displayName||T.name||"",H=H!==""?"ForwardRef("+H+")":"ForwardRef"),H;case h:return T=H.displayName||null,T!==null?T:X(H.type)||"Memo";case G4:T=H._payload,H=H._init;try{return X(H(T))}catch(x){}}return null}function Q(H){return""+H}function Z(H){try{Q(H);var T=!1}catch(j4){T=!0}if(T){T=console;var x=T.error,p=typeof Symbol==="function"&&Symbol.toStringTag&&H[Symbol.toStringTag]||H.constructor.name||"Object";return x.call(T,"The provided key is an unsupported type %s. This value must be coerced to a string before using it here.",p),Q(H)}}function Y(H){if(H===R)return"<>";if(typeof H==="object"&&H!==null&&H.$$typeof===G4)return"<...>";try{var T=X(H);return T?"<"+T+">":"<...>"}catch(x){return"<...>"}}function J(){var H=Y4.A;return H===null?null:H.getOwner()}function W(){return Error("react-stack-top-frame")}function G(H){if(q4.call(H,"key")){var T=Object.getOwnPropertyDescriptor(H,"key").get;if(T&&T.isReactWarning)return!1}return H.key!==void 0}function q(H,T){function x(){E4||(E4=!0,console.error("%s: `key` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://react.dev/link/special-props)",T))}x.isReactWarning=!0,Object.defineProperty(H,"key",{get:x,configurable:!0})}function U(){var H=X(this.type);return W4[H]||(W4[H]=!0,console.error("Accessing element.ref was removed in React 19. ref is now a regular prop. It will be removed from the JSX Element type in a future release.")),H=this.props.ref,H!==void 0?H:null}function A(H,T,x,p,j4,D4){var c=x.ref;return H={$$typeof:j,type:H,key:T,props:x,_owner:p},(c!==void 0?c:null)!==null?Object.defineProperty(H,"ref",{enumerable:!1,get:U}):Object.defineProperty(H,"ref",{enumerable:!1,value:null}),H._store={},Object.defineProperty(H._store,"validated",{configurable:!1,enumerable:!1,writable:!0,value:0}),Object.defineProperty(H,"_debugInfo",{configurable:!1,enumerable:!1,writable:!0,value:null}),Object.defineProperty(H,"_debugStack",{configurable:!1,enumerable:!1,writable:!0,value:j4}),Object.defineProperty(H,"_debugTask",{configurable:!1,enumerable:!1,writable:!0,value:D4}),Object.freeze&&(Object.freeze(H.props),Object.freeze(H)),H}function M(H,T,x,p,j4,D4){var c=T.children;if(c!==void 0)if(p)if(t(c)){for(p=0;p<c.length;p++)O(c[p]);Object.freeze&&Object.freeze(c)}else console.error("React.jsx: Static children should always be an array. You are likely explicitly calling React.jsxs or React.jsxDEV. Use the Babel transform instead.");else O(c);if(q4.call(T,"key")){c=X(H);var Z4=Object.keys(T).filter(function(b4){return b4!=="key"});p=0<Z4.length?"{key: someKey, "+Z4.join(": ..., ")+": ...}":"{key: someKey}",N4[c+p]||(Z4=0<Z4.length?"{"+Z4.join(": ..., ")+": ...}":"{}",console.error(`A props object containing a "key" prop is being spread into JSX:
  let props = %s;
  <%s {...props} />
React keys must be passed directly to JSX without using spread:
  let props = %s;
  <%s key={someKey} {...props} />`,p,c,Z4,c),N4[c+p]=!0)}if(c=null,x!==void 0&&(Z(x),c=""+x),G(T)&&(Z(T.key),c=""+T.key),"key"in T){x={};for(var T4 in T)T4!=="key"&&(x[T4]=T[T4])}else x=T;return c&&q(x,typeof H==="function"?H.displayName||H.name||"Unknown":H),A(H,c,x,J(),j4,D4)}function O(H){z(H)?H._store&&(H._store.validated=1):typeof H==="object"&&H!==null&&H.$$typeof===G4&&(H._payload.status==="fulfilled"?z(H._payload.value)&&H._payload.value._store&&(H._payload.value._store.validated=1):H._store&&(H._store.validated=1))}function z(H){return typeof H==="object"&&H!==null&&H.$$typeof===j}var j=Symbol.for("react.transitional.element"),B=Symbol.for("react.portal"),R=Symbol.for("react.fragment"),D=Symbol.for("react.strict_mode"),b=Symbol.for("react.profiler"),w=Symbol.for("react.consumer"),F=Symbol.for("react.context"),V=Symbol.for("react.forward_ref"),k=Symbol.for("react.suspense"),P=Symbol.for("react.suspense_list"),h=Symbol.for("react.memo"),G4=Symbol.for("react.lazy"),z4=Symbol.for("react.activity"),d=Symbol.for("react.client.reference"),Y4=I5.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,q4=Object.prototype.hasOwnProperty,t=Array.isArray,e=console.createTask?console.createTask:function(){return null};I5={react_stack_bottom_frame:function(H){return H()}};var E4,W4={},B4=I5.react_stack_bottom_frame.bind(I5,W)(),$4=e(Y(W)),N4={};WX.Fragment=R,WX.jsxDEV=function(H,T,x,p){var j4=1e4>Y4.recentlyCreatedOwnerStacks++;return M(H,T,x,p,j4?Error("react-stack-top-frame"):B4,j4?e(Y(H)):$4)}})()});var q9=d7((qX)=>{var u5=W6(J6());(function(){function X(H){if(H==null)return null;if(typeof H==="function")return H.$$typeof===d?null:H.displayName||H.name||null;if(typeof H==="string")return H;switch(H){case R:return"Fragment";case b:return"Profiler";case D:return"StrictMode";case k:return"Suspense";case P:return"SuspenseList";case z4:return"Activity"}if(typeof H==="object")switch(typeof H.tag==="number"&&console.error("Received an unexpected object in getComponentNameFromType(). This is likely a bug in React. Please file an issue."),H.$$typeof){case B:return"Portal";case F:return H.displayName||"Context";case w:return(H._context.displayName||"Context")+".Consumer";case V:var T=H.render;return H=H.displayName,H||(H=T.displayName||T.name||"",H=H!==""?"ForwardRef("+H+")":"ForwardRef"),H;case h:return T=H.displayName||null,T!==null?T:X(H.type)||"Memo";case G4:T=H._payload,H=H._init;try{return X(H(T))}catch(x){}}return null}function Q(H){return""+H}function Z(H){try{Q(H);var T=!1}catch(j4){T=!0}if(T){T=console;var x=T.error,p=typeof Symbol==="function"&&Symbol.toStringTag&&H[Symbol.toStringTag]||H.constructor.name||"Object";return x.call(T,"The provided key is an unsupported type %s. This value must be coerced to a string before using it here.",p),Q(H)}}function Y(H){if(H===R)return"<>";if(typeof H==="object"&&H!==null&&H.$$typeof===G4)return"<...>";try{var T=X(H);return T?"<"+T+">":"<...>"}catch(x){return"<...>"}}function J(){var H=Y4.A;return H===null?null:H.getOwner()}function W(){return Error("react-stack-top-frame")}function G(H){if(q4.call(H,"key")){var T=Object.getOwnPropertyDescriptor(H,"key").get;if(T&&T.isReactWarning)return!1}return H.key!==void 0}function q(H,T){function x(){E4||(E4=!0,console.error("%s: `key` is not a prop. Trying to access it will result in `undefined` being returned. If you need to access the same value within the child component, you should pass it as a different prop. (https://react.dev/link/special-props)",T))}x.isReactWarning=!0,Object.defineProperty(H,"key",{get:x,configurable:!0})}function U(){var H=X(this.type);return W4[H]||(W4[H]=!0,console.error("Accessing element.ref was removed in React 19. ref is now a regular prop. It will be removed from the JSX Element type in a future release.")),H=this.props.ref,H!==void 0?H:null}function A(H,T,x,p,j4,D4){var c=x.ref;return H={$$typeof:j,type:H,key:T,props:x,_owner:p},(c!==void 0?c:null)!==null?Object.defineProperty(H,"ref",{enumerable:!1,get:U}):Object.defineProperty(H,"ref",{enumerable:!1,value:null}),H._store={},Object.defineProperty(H._store,"validated",{configurable:!1,enumerable:!1,writable:!0,value:0}),Object.defineProperty(H,"_debugInfo",{configurable:!1,enumerable:!1,writable:!0,value:null}),Object.defineProperty(H,"_debugStack",{configurable:!1,enumerable:!1,writable:!0,value:j4}),Object.defineProperty(H,"_debugTask",{configurable:!1,enumerable:!1,writable:!0,value:D4}),Object.freeze&&(Object.freeze(H.props),Object.freeze(H)),H}function M(H,T,x,p,j4,D4){var c=T.children;if(c!==void 0)if(p)if(t(c)){for(p=0;p<c.length;p++)O(c[p]);Object.freeze&&Object.freeze(c)}else console.error("React.jsx: Static children should always be an array. You are likely explicitly calling React.jsxs or React.jsxDEV. Use the Babel transform instead.");else O(c);if(q4.call(T,"key")){c=X(H);var Z4=Object.keys(T).filter(function(b4){return b4!=="key"});p=0<Z4.length?"{key: someKey, "+Z4.join(": ..., ")+": ...}":"{key: someKey}",N4[c+p]||(Z4=0<Z4.length?"{"+Z4.join(": ..., ")+": ...}":"{}",console.error(`A props object containing a "key" prop is being spread into JSX:
  let props = %s;
  <%s {...props} />
React keys must be passed directly to JSX without using spread:
  let props = %s;
  <%s key={someKey} {...props} />`,p,c,Z4,c),N4[c+p]=!0)}if(c=null,x!==void 0&&(Z(x),c=""+x),G(T)&&(Z(T.key),c=""+T.key),"key"in T){x={};for(var T4 in T)T4!=="key"&&(x[T4]=T[T4])}else x=T;return c&&q(x,typeof H==="function"?H.displayName||H.name||"Unknown":H),A(H,c,x,J(),j4,D4)}function O(H){z(H)?H._store&&(H._store.validated=1):typeof H==="object"&&H!==null&&H.$$typeof===G4&&(H._payload.status==="fulfilled"?z(H._payload.value)&&H._payload.value._store&&(H._payload.value._store.validated=1):H._store&&(H._store.validated=1))}function z(H){return typeof H==="object"&&H!==null&&H.$$typeof===j}var j=Symbol.for("react.transitional.element"),B=Symbol.for("react.portal"),R=Symbol.for("react.fragment"),D=Symbol.for("react.strict_mode"),b=Symbol.for("react.profiler"),w=Symbol.for("react.consumer"),F=Symbol.for("react.context"),V=Symbol.for("react.forward_ref"),k=Symbol.for("react.suspense"),P=Symbol.for("react.suspense_list"),h=Symbol.for("react.memo"),G4=Symbol.for("react.lazy"),z4=Symbol.for("react.activity"),d=Symbol.for("react.client.reference"),Y4=u5.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,q4=Object.prototype.hasOwnProperty,t=Array.isArray,e=console.createTask?console.createTask:function(){return null};u5={react_stack_bottom_frame:function(H){return H()}};var E4,W4={},B4=u5.react_stack_bottom_frame.bind(u5,W)(),$4=e(Y(W)),N4={};qX.Fragment=R,qX.jsx=function(H,T,x){var p=1e4>Y4.recentlyCreatedOwnerStacks++;return M(H,T,x,!1,p?Error("react-stack-top-frame"):B4,p?e(Y(H)):$4)},qX.jsxs=function(H,T,x){var p=1e4>Y4.recentlyCreatedOwnerStacks++;return M(H,T,x,!0,p?Error("react-stack-top-frame"):B4,p?e(Y(H)):$4)}})()});var D5="file-tree-container",f6="data-file-tree-style",s7="data-file-tree-unsafe-css",W9="data-file-tree-scrollbar-measure",i7="data-file-tree-scrollbar-gutter-measured",G9="--trees-scrollbar-gutter-measured",o7="f::",m5="header",k5="context-menu",q7="context-menu-trigger";var g4=W6(J6(),1),r4=W6(q9(),1),$9=typeof window>"u"?g4.useEffect:g4.useLayoutEffect;function $X(X,Q,Z){let Y=X!=null?r4.jsx("div",{slot:m5,children:X}):null,J=Q!=null&&Z!=null?r4.jsx("div",{slot:k5,children:Q(Z.item,Z.context)}):null;if(Y==null&&J==null)return null;return r4.jsxs(r4.Fragment,{children:[Y,J]})}function UX(X,Q){if(typeof window>"u"&&Q!=null)return r4.jsxs(r4.Fragment,{children:[r4.jsx("template",{shadowrootmode:"open",dangerouslySetInnerHTML:{__html:Q.shadowHtml}}),X]});return r4.jsx(r4.Fragment,{children:X})}function zX(X){let Q=X.shadowRoot;if(Q?.querySelector("[data-file-tree-id]")instanceof HTMLElement||Q?.querySelector("[data-file-tree-id]")instanceof SVGElement)return!0;return X.querySelector('template[shadowrootmode="open"]')instanceof HTMLTemplateElement}function KX(X,Q,Z,Y,J){let W={...X??{}};if(Q!=null)delete W.header;if(Z){let G=X?.contextMenu,q=G?.onClose,U=G?.onOpen;W.contextMenu={...G??{},enabled:!0,onClose:()=>{q?.(),Y()},onOpen:(A,M)=>{J(A,M),U?.(A,M)}},delete W.contextMenu.render}return W.header!=null||W.contextMenu!=null?W:void 0}function MX({header:X,id:Q,model:Z,preloadedData:Y,renderContextMenu:J,...W}){let[G,q]=g4.useState(null),[U,A]=g4.useState(null),M=g4.useRef(Z.getComposition()),O=g4.useRef(Z);if(O.current!==Z)O.current=Z,M.current=Z.getComposition();let z=J!=null,j=g4.useCallback(()=>{q(null)},[]),B=g4.useCallback((k,P)=>{q({context:P,item:k})},[]),R=M.current,D=g4.useMemo(()=>KX(R,X,z,j,B),[R,j,B,z,X]),b=g4.useCallback((k)=>{A(k)},[]);g4.useEffect(()=>{if(z)return;q(null)},[z]),$9(()=>{Z.setComposition(D)},[D,Z]),$9(()=>{if(U==null)return;if(Y!=null&&zX(U))Z.hydrate({fileTreeContainer:U});else Z.render({fileTreeContainer:U});return()=>{Z.unmount(),Z.setComposition(R)}},[R,U,Z,Y]);let w=UX($X(X,J,G),Y),F=Q??Y?.id,V={["--trees-item-height"]:`${String(Z.getItemHeight())}px`,["--trees-density-override"]:Z.getDensityFactor(),...W.style};return r4.jsx(D5,{...W,id:F,ref:b,style:V,suppressHydrationWarning:Y!=null,children:w})}var HX=[`<symbol id="file-tree-builtin-bash" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8 1C2.24 1 1 2.24 1 8s1.24 7 7 7 7-1.24 7-7-1.24-7-7-7" class="bg" opacity=".2"/>
  <path fill="currentColor" d="M11.5 11a.5.5 0 0 1 0 1h-3a.5.5 0 0 1 0-1zM7 6.75C7 6.42 6.64 6 6 6s-1 .42-1 .75q-.01.25.22.41.26.21.89.35.74.14 1.28.53c.37.29.61.7.61 1.21 0 .87-.68 1.5-1.5 1.7v.55a.5.5 0 0 1-1 0v-.56c-.82-.18-1.5-.82-1.5-1.69a.5.5 0 0 1 1 0c0 .33.36.75 1 .75s1-.42 1-.75q.01-.25-.22-.41a2 2 0 0 0-.89-.35q-.74-.14-1.28-.53A1.5 1.5 0 0 1 4 6.75c0-.87.68-1.5 1.5-1.7V4.5a.5.5 0 0 1 1 0v.56c.82.18 1.5.82 1.5 1.69a.5.5 0 0 1-1 0" class="fg-stroke"/>
</symbol>`,`<symbol id="file-tree-builtin-css" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8 15c-5.76 0-7-1.24-7-7V2a1 1 0 0 1 1-1h6c5.77 0 7 1.24 7 7s-1.24 7-7 7" class="vector" opacity=".2"/>
  <path fill="currentColor" d="M10.1 9.19h.73c.03.49.22.6 1 .6.76 0 .93-.12.93-.68 0-.52-.17-.67-.94-.85-1.38-.3-1.68-.56-1.68-1.47 0-1.05.3-1.29 1.67-1.29 1.29 0 1.57.2 1.6 1.13h-.74c-.01-.34-.17-.42-.85-.42-.77 0-.94.1-.94.58 0 .42.17.55.96.73 1.36.3 1.66.58 1.66 1.59 0 1.14-.31 1.39-1.73 1.39-1.39 0-1.69-.24-1.67-1.31m-3.9 0h.74c.03.49.21.6.99.6.76 0 .93-.12.93-.68 0-.52-.17-.67-.93-.85-1.39-.3-1.69-.56-1.69-1.47 0-1.05.3-1.29 1.67-1.29 1.3 0 1.58.2 1.6 1.13h-.73c-.02-.34-.18-.42-.85-.42-.78 0-.95.1-.95.58 0 .42.17.55.96.73 1.37.3 1.67.58 1.67 1.59 0 1.14-.32 1.39-1.74 1.39-1.38 0-1.68-.24-1.66-1.31m-1.22 0h.75c-.09 1.07-.37 1.31-1.56 1.31-1.37 0-1.68-.45-1.68-2.5 0-1.96.36-2.5 1.68-2.5 1.16 0 1.44.25 1.52 1.35h-.76c-.08-.52-.22-.64-.76-.64-.74 0-.9.33-.9 1.78 0 1.47.16 1.8.9 1.8.58 0 .74-.11.8-.6"/>
</symbol>`,`<symbol id="file-tree-builtin-database" viewBox="0 0 16 16">
  <path fill="currentColor" d="M14.953 9.733a12.4 12.4 0 0 1-.244 1.936c-.207.933-.532 1.58-.996 2.044s-1.11.789-2.044.996C10.73 14.918 9.533 15 8 15s-2.73-.082-3.669-.291c-.933-.207-1.58-.532-2.044-.996s-.789-1.11-.996-2.044c-.122-.547-.2-1.182-.244-1.92q.23.364.532.667c.64.639 1.482 1.031 2.533 1.265 1.046.232 2.33.315 3.884.315 1.555 0 2.838-.083 3.884-.315 1.051-.234 1.893-.626 2.532-1.265a4 4 0 0 0 .541-.683"/>
  <path fill="currentColor" d="M14.93 5.924c-.046.663-.118 1.24-.23 1.743-.207.932-.532 1.579-.995 2.042s-1.11.789-2.042.996c-.938.209-2.135.291-3.667.291-1.531 0-2.729-.082-3.667-.29-.932-.208-1.579-.534-2.042-.997s-.789-1.11-.996-2.042a12 12 0 0 1-.227-1.683l.016-.188a4 4 0 0 0 .5.62c.638.639 1.48 1.031 2.532 1.265 1.046.232 2.33.315 3.884.315 1.555 0 2.838-.083 3.884-.315 1.051-.234 1.893-.626 2.532-1.265.192-.192.357-.404.506-.633z"/>
  <path fill="currentColor" d="M8 1c1.533 0 2.73.082 3.669.291.933.207 1.58.533 2.044.996.403.404.904.944.91 1.695.004.764-.509 1.318-.918 1.727-.463.463-1.11.789-2.042.996-.938.209-2.135.291-3.667.291-1.531 0-2.729-.082-3.667-.29-.932-.208-1.579-.534-2.042-.997-.406-.406-.915-.953-.915-1.71 0-.758.509-1.305.915-1.712.464-.463 1.11-.789 2.044-.996C5.27 1.082 6.467 1 8 1"/>
</symbol>`,`<symbol id="file-tree-builtin-default" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8 1v3a3 3 0 0 0 3 3h3v5.5a2.5 2.5 0 0 1-2.5 2.5h-7A2.5 2.5 0 0 1 2 12.5v-9A2.5 2.5 0 0 1 4.5 1z" class="bg" opacity=".4"/>
  <path fill="currentColor" d="M9.5 1a.5.5 0 0 1 .354.146l4 4A.5.5 0 0 1 14 5.5V6h-3a2 2 0 0 1-2-2V1z" class="fg"/>
</symbol>`,`<symbol id="file-tree-builtin-font" viewBox="0 0 16 16">
  <path fill="currentColor" d="M12.3 13c-1.59 0-2.68-.99-2.68-2.5 0-1.43 1-2.34 2.88-2.35h2.16v-.83c0-1.08-.62-1.68-1.73-1.68-1.05 0-1.66.54-1.73 1.36H9.93c.09-1.43 1.06-2.48 3.05-2.48 1.75 0 3.02.95 3.02 2.68v5.66h-1.29v-1.02h-.04c-.41.66-1.16 1.16-2.37 1.16m.36-1.12c1.14 0 2-.72 2-1.74v-.96H12.6c-1.12 0-1.6.54-1.6 1.28 0 .97.8 1.42 1.66 1.42m-11.24.98H0L3.8 2h1.39l3.8 10.86H7.54l-1.08-3.2H2.5zm3.09-9.25h-.04l-1.6 4.95H6.1z"/>
</symbol>`,`<symbol id="file-tree-builtin-git" viewBox="0 0 16 16">
  <path fill="currentColor" d="M14.74 7.38 8.62 1.26a.9.9 0 0 0-1.27 0L6.08 2.53l1.61 1.61a1.07 1.07 0 0 1 1.36 1.37l1.55 1.55a1.07 1.07 0 0 1 1.1 1.77 1.07 1.07 0 0 1-1.74-1.16L8.5 6.22v3.8a1.07 1.07 0 1 1-.89-.02V6.15a1.07 1.07 0 0 1-.58-1.4l-1.58-1.6-4.2 4.2a.9.9 0 0 0 0 1.27l6.12 6.12a.9.9 0 0 0 1.27 0l6.09-6.09a.9.9 0 0 0 0-1.27"/>
</symbol>`,`<symbol id="file-tree-builtin-go" viewBox="0 0 16 16">
  <path fill="currentColor" fill-rule="evenodd" d="M4.41 4.57A3.2 3.2 0 0 1 6.87 5q.74.49 1.08 1.29.08.12-.1.16l-1.55.4c-.14.03-.15.04-.27-.1a1 1 0 0 0-.44-.34 1.6 1.6 0 0 0-1.68.14q-.95.61-.94 1.73c0 .73.52 1.33 1.25 1.43q.95.1 1.58-.6l.25-.34h-1.8c-.19 0-.24-.12-.17-.27.12-.28.34-.76.47-1a.3.3 0 0 1 .24-.14h2.98a4 4 0 0 1 .64-1.19 4 4 0 0 1 2.6-1.52 3.5 3.5 0 0 1 2.64.46q1.13.73 1.31 2.04a3.5 3.5 0 0 1-1.06 3.09q-.93.92-2.23 1.17l-.74.08a3.5 3.5 0 0 1-2.27-.8 3 3 0 0 1-.93-1.42 4 4 0 0 1-.39.61 4 4 0 0 1-2.64 1.56 3.3 3.3 0 0 1-2.5-.6 3 3 0 0 1-1.18-2.03 3.5 3.5 0 0 1 .8-2.67 4 4 0 0 1 2.6-1.58M13.1 7.5a1.53 1.53 0 0 0-1.9-1.21q-1.3.3-1.62 1.59a1.5 1.5 0 0 0 .85 1.72q.77.33 1.52-.05a2 2 0 0 0 1.18-1.74q0-.17-.03-.3" clip-rule="evenodd"/>
</symbol>`,`<symbol id="file-tree-builtin-html" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8 1C2.24 1 1 2.24 1 8s1.24 7 7 7 7-1.24 7-7-1.24-7-7-7" class="bg" opacity=".2"/>
  <path fill="currentColor" d="M10.48 3.76a.5.5 0 0 1 .4.58L10.6 5.8h1.14a.5.5 0 0 1 0 1h-1.32L10 9.2h1.08a.5.5 0 0 1 0 1H9.8l-.3 1.64a.5.5 0 1 1-.98-.18l.27-1.46H6.4l-.3 1.64a.5.5 0 1 1-.98-.18l.27-1.46H4.25a.5.5 0 0 1 0-1h1.32L6 6.8H4.93a.5.5 0 0 1 0-1H6.2l.3-1.64a.5.5 0 1 1 .98.18L7.2 5.8h2.4l.3-1.64a.5.5 0 0 1 .58-.4M6.58 9.2h2.4l.44-2.4h-2.4z" class="fg"/>
</symbol>`,`<symbol id="file-tree-builtin-image" viewBox="0 0 16 16">
  <path fill="currentColor" d="M12.5 2A2.5 2.5 0 0 1 15 4.5v4.67l-4.05-3.54-4.08 4.08-3-2L1 10.6V4.5A2.5 2.5 0 0 1 3.5 2z" opacity=".3"/>
  <path fill="currentColor" d="M15 10.5v1a2.5 2.5 0 0 1-2.5 2.5h-9a2.5 2.5 0 0 1-2.46-2.04L4 9l3 2 4-4zm-7-5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0"/>
</symbol>`,`<symbol id="file-tree-builtin-javascript" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8 1C2.24 1 1 2.24 1 8s1.24 7 7 7 7-1.24 7-7-1.24-7-7-7" class="bg" opacity=".2"/>
  <path fill="currentColor" d="M8.1 9.64h.95c.04.62.28.76 1.28.76s1.2-.14 1.2-.85c0-.66-.2-.85-1.2-1.07-1.79-.38-2.18-.7-2.18-1.86C8.15 5.3 8.54 5 10.31 5c1.67 0 2.04.26 2.07 1.42h-.95c-.02-.43-.23-.53-1.1-.53-1 0-1.22.14-1.22.74 0 .52.22.7 1.24.92 1.76.38 2.15.73 2.15 2 0 1.44-.4 1.75-2.24 1.75-1.8 0-2.18-.3-2.15-1.66M3.5 9.5h.98c0 .76.15.92.85.92.77 0 .94-.18.94-1.02V5.1h1v4.34c0 1.54-.35 1.87-1.92 1.87-1.55 0-1.89-.32-1.86-1.8"/>
</symbol>`,`<symbol id="file-tree-builtin-json" viewBox="0 0 16 16">
  <path fill="currentColor" d="M13.25 11.5V9.75a.5.5 0 0 1 .36-.48l.55-.15a1.16 1.16 0 0 0 0-2.24l-.55-.15a.5.5 0 0 1-.36-.48V4.5a2.5 2.5 0 0 0-2.5-2.5h-.25a.5.5 0 0 0 0 1h.25a1.5 1.5 0 0 1 1.5 1.5v1.75a1.5 1.5 0 0 0 1.09 1.44l.54.15a.16.16 0 0 1 0 .32l-.54.15a1.5 1.5 0 0 0-1.09 1.44v1.75a1.5 1.5 0 0 1-1.5 1.5h-.25a.5.5 0 0 0 0 1h.25a2.5 2.5 0 0 0 2.5-2.5m-10.5 0V9.75a.5.5 0 0 0-.36-.48l-.55-.15a1.16 1.16 0 0 1 0-2.24l.55-.15a.5.5 0 0 0 .36-.48V4.5A2.5 2.5 0 0 1 5.25 2h.25a.5.5 0 0 1 0 1h-.25a1.5 1.5 0 0 0-1.5 1.5v1.75a1.5 1.5 0 0 1-1.09 1.44l-.54.15a.16.16 0 0 0 0 .32l.54.15a1.5 1.5 0 0 1 1.09 1.45v1.74a1.5 1.5 0 0 0 1.5 1.5h.25a.5.5 0 0 1 0 1h-.25a2.5 2.5 0 0 1-2.5-2.5"/>
</symbol>`,`<symbol id="file-tree-builtin-markdown" viewBox="0 0 16 16">
  <path fill="currentColor" d="M1 12V4h2l2 2.5L7 4h2v8H7V7.5l-2 2-2-2V12zm9-3 3 3.5L16 9h-2V4h-2v5z"/>
</symbol>`,`<symbol id="file-tree-builtin-mcp" viewBox="0 0 16 16">
  <path fill="currentColor" d="M9.26-.04a3 3 0 0 1 2 .82 2.8 2.8 0 0 1 .8 2.35 2.9 2.9 0 0 1 2.41.8l.03.02a2.74 2.74 0 0 1 0 3.94l-5.8 5.69-.04.06-.02.07q0 .04.02.07.01.04.04.06l1.2 1.17a.55.55 0 0 1 0 .79.6.6 0 0 1-.81 0l-1.2-1.17a1.3 1.3 0 0 1 0-1.84L13.7 7.1a1.65 1.65 0 0 0 .37-1.82 2 2 0 0 0-.37-.54l-.03-.03a1.73 1.73 0 0 0-2.4 0L6.47 9.4l-.07.06a.58.58 0 0 1-.92-.18.6.6 0 0 1 .12-.6l4.85-4.76a1.65 1.65 0 0 0 0-2.36 1.73 1.73 0 0 0-2.4 0l-6.43 6.3a.6.6 0 0 1-.8 0 .55.55 0 0 1 0-.8L7.25.79a3 3 0 0 1 2-.82"/>
  <path fill="currentColor" d="M9.26 2.19a.6.6 0 0 1 .52.34.6.6 0 0 1 0 .43l-.12.18L4.9 7.79a1.65 1.65 0 0 0 0 2.36 1.73 1.73 0 0 0 2.4 0l4.75-4.66a.58.58 0 0 1 .93.18.6.6 0 0 1-.12.61l-4.75 4.66a2.9 2.9 0 0 1-4.01 0 2.75 2.75 0 0 1-.62-3.04A3 3 0 0 1 4.1 7l4.74-4.65a.6.6 0 0 1 .4-.16"/>
</symbol>`,`<symbol id="file-tree-builtin-python" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8.33 8.4H10c1.16 0 1.9-.73 1.9-1.86V5.08q0-.24.25-.24h.74c.75 0 1.33.32 1.66.97q.4.73.41 1.46c.09.9.09 1.78-.24 2.67-.25.73-.75 1.3-1.58 1.46h-4.8c-.08 0-.25 0-.25.08v.4s.17.09.25.09h2.82q.34-.02.33.32v1.06c0 .56-.25.97-.75 1.13-.41.16-.83.33-1.24.4a7 7 0 0 1-2.98-.07 3 3 0 0 1-1.16-.49c-.33-.32-.58-.65-.5-1.14v-2.91c0-1.13.67-1.78 1.82-1.78q.89-.1 1.66-.08m2.32 4.86a.65.65 0 0 0-.66-.65c-.34 0-.67.33-.67.65s.33.57.67.65a.65.65 0 0 0 .66-.65" class="bg" opacity=".8"/>
  <path fill="currentColor" d="M7.67 7.6H6c-1.16 0-1.9.73-1.9 1.86v1.46q0 .24-.25.24h-.74c-.75 0-1.33-.32-1.66-.97a3 3 0 0 1-.41-1.46 6 6 0 0 1 .24-2.67c.25-.73.75-1.3 1.58-1.46h4.8c.08 0 .25 0 .25-.08v-.4s-.17-.09-.25-.09H4.85c-.24 0-.33-.08-.33-.32V2.65c0-.56.25-.97.75-1.13.41-.16.83-.33 1.24-.4a7 7 0 0 1 2.98.07c.41.09.83.25 1.16.49.33.32.58.65.5 1.13v2.92c0 1.14-.67 1.78-1.82 1.78-.58.08-1.16.08-1.66.08M5.35 2.73c0 .33.25.65.66.65.33 0 .66-.32.66-.65 0-.32-.33-.56-.66-.64a.65.65 0 0 0-.66.64" class="fg"/>
</symbol>`,`<symbol id="file-tree-builtin-ruby" viewBox="0 0 16 16">
  <path fill="currentColor" fill-rule="evenodd" d="M11.04 2c.48 0 .92.23 1.18.6l2.54 3.65c.37.52.3 1.23-.15 1.69l-5.58 5.64a1.47 1.47 0 0 1-2.06 0L1.39 7.94a1.3 1.3 0 0 1-.15-1.7l2.54-3.63q.2-.3.5-.45.33-.16.68-.16zm.84 2.17a.5.5 0 0 0-.7-.05L8 6.84 4.83 4.12a.5.5 0 0 0-.65.76L6.65 7H3.5a.5.5 0 0 0 0 1h9a.5.5 0 0 0 0-1H9.35l2.48-2.12a.5.5 0 0 0 .05-.7" clip-rule="evenodd"/>
</symbol>`,`<symbol id="file-tree-builtin-rust" viewBox="0 0 16 16">
  <path fill="currentColor" fill-rule="evenodd" d="M8 .8a.2.2 0 0 1 .18.1l.38.6.16.02.5-.53.01-.01a.2.2 0 0 1 .33.08l.25.68.16.05.59-.43h.02a.2.2 0 0 1 .3.14l.12.71.15.08.65-.3a.2.2 0 0 1 .2.02.2.2 0 0 1 .1.18l-.03.72.12.1.71-.16a.2.2 0 0 1 .25.25l-.17.7q.06.06.1.13l.73-.03A.2.2 0 0 1 14 4a.2.2 0 0 1 .02.2l-.3.66.08.14.71.12a.2.2 0 0 1 .14.32l-.43.59.05.16.68.25a.2.2 0 0 1 .07.35l-.53.49.01.16.62.38a.2.2 0 0 1 0 .36l-.62.38-.01.16.53.5a.2.2 0 0 1-.07.34l-.68.25-.05.16.43.59a.2.2 0 0 1-.14.32l-.72.12-.07.15.3.65a.2.2 0 0 1-.02.2.2.2 0 0 1-.18.1l-.72-.03-.1.13.16.7a.2.2 0 0 1-.25.25l-.7-.17-.13.1.03.73a.2.2 0 0 1-.1.18.2.2 0 0 1-.2.02l-.66-.3-.14.08-.12.71a.2.2 0 0 1-.32.14l-.59-.43-.16.05-.25.68a.2.2 0 0 1-.34.07l-.5-.53-.16.01-.38.62a.2.2 0 0 1-.36 0l-.38-.62-.16-.01-.5.53a.2.2 0 0 1-.34-.07l-.25-.68-.16-.05-.59.43a.2.2 0 0 1-.32-.14L5 13.78l-.15-.07-.65.3a.2.2 0 0 1-.2-.02.2.2 0 0 1-.1-.18l.03-.72-.13-.1-.7.16a.2.2 0 0 1-.25-.25l.17-.7-.1-.13-.73.03a.2.2 0 0 1-.2-.3l.3-.66-.08-.14-.71-.12a.2.2 0 0 1-.14-.32l.43-.59-.05-.16-.68-.25A.2.2 0 0 1 1 9.22l.53-.5-.02-.16-.6-.38A.2.2 0 0 1 .8 8a.2.2 0 0 1 .1-.18l.6-.38.02-.16-.53-.5a.2.2 0 0 1 .07-.34l.68-.25.05-.16-.43-.59a.2.2 0 0 1 .14-.32L2.2 5l.08-.15L2 4.2a.2.2 0 0 1 .2-.3l.72.03.1-.13-.16-.7a.2.2 0 0 1 .25-.25l.7.16.13-.1-.03-.72A.2.2 0 0 1 4 2a.2.2 0 0 1 .2-.02l.65.3L5 2.2l.12-.71v-.03a.2.2 0 0 1 .32-.1l.59.41.16-.04.25-.68.01-.02A.2.2 0 0 1 6.8.99l.49.53.16-.02.38-.61.02-.02A.2.2 0 0 1 8 .79M6.8 9.45h1.26l.06.01q.03.01.03.05v1.52q0 .07-.09.06h-4.5A5.4 5.4 0 0 0 8 13.42a5.4 5.4 0 0 0 4.45-2.33h-2.42c-.36 0-.68-.5-.77-.75-.08-.22-.2-.91-.25-1.12-.15-.61-.59-.71-.78-.73H6.8zM8 2.58a5.4 5.4 0 0 0-4.07 1.85h5.74l.17.02c.23.03.6.12.96.35.34.23.83.68.83 1.4 0 .66-.55 1.16-1.08 1.5.42.33.7.53.86 1.44.04.17.34.32.62.29.29-.03.62-.16.62-.75v-.24q0-.1.07-.1h.68A5.43 5.43 0 0 0 8 2.59M2.96 6.03a5.4 5.4 0 0 0-.19 3.37h1.66V6.03zM6.8 7.06h1.66c.35 0 .77-.12.77-.47 0-.42-.55-.53-.65-.53H6.8z" clip-rule="evenodd"/>
</symbol>`,`<symbol id="file-tree-builtin-swift" viewBox="0 0 16 16">
  <path fill="currentColor" d="M9.63 1c6.15 4.35 4.16 9.15 4.16 9.15s1.75 2.05 1.04 3.85c0 0-.72-1.26-1.93-1.26-1.17 0-1.85 1.26-4.2 1.26C3.47 14 1 9.46 1 9.46c4.71 3.22 7.93.94 7.93.94C6.8 9.12 2.29 3 2.29 3c3.93 3.47 5.63 4.39 5.63 4.39-1.01-.87-3.86-5.13-3.86-5.13C6.34 4.66 10.86 8 10.86 8c1.28-3.7-1.23-7-1.23-7"/>
</symbol>`,`<symbol id="file-tree-builtin-table" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8 4a3 3 0 0 0 3 3h3v5.5a2.5 2.5 0 0 1-2.5 2.5h-7A2.5 2.5 0 0 1 2 12.5v-9A2.5 2.5 0 0 1 4.5 1H8z" class="bg" opacity=".4"/>
  <path fill="currentColor" d="M11.5 8a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-.5.5h-7a.5.5 0 0 1-.5-.5v-4a.5.5 0 0 1 .5-.5zM5 12h2.5v-1H5zm3.5 0H11v-1H8.5zM5 10h2.5V9H5zm3.5 0H11V9H8.5zm1-9a.5.5 0 0 1 .354.146l4 4A.5.5 0 0 1 14 5.5V6h-3a2 2 0 0 1-2-2V1z" class="fg"/>
</symbol>`,`<symbol id="file-tree-builtin-text" viewBox="0 0 16 16">
  <path fill="currentColor" fill-rule="evenodd" d="M8 4a3 3 0 0 0 3 3h3v5.5a2.5 2.5 0 0 1-2.5 2.5h-7A2.5 2.5 0 0 1 2 12.5v-9A2.5 2.5 0 0 1 4.5 1H8z" class="bg" clip-rule="evenodd" opacity=".4"/>
  <path fill="currentColor" d="M8.5 11a.5.5 0 0 1 0 1h-3a.5.5 0 0 1 0-1zm2-2a.5.5 0 0 1 0 1h-5a.5.5 0 0 1 0-1zm-1-8a.5.5 0 0 1 .354.146l4 4A.5.5 0 0 1 14 5.5V6h-3a2 2 0 0 1-2-2V1z"/>
</symbol>`,`<symbol id="file-tree-builtin-typescript" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8 1C2.24 1 1 2.24 1 8s1.24 7 7 7 7-1.24 7-7-1.24-7-7-7" class="bg" opacity=".2"/>
  <path fill="currentColor" d="M8.1 9.64h.95c.04.62.28.76 1.28.76s1.2-.14 1.2-.85c0-.66-.2-.85-1.2-1.07-1.79-.38-2.18-.7-2.18-1.86C8.15 5.3 8.54 5 10.31 5c1.67 0 2.04.26 2.07 1.42h-.95c-.02-.43-.23-.53-1.1-.53-1 0-1.22.14-1.22.74 0 .52.22.7 1.24.92 1.76.38 2.15.73 2.15 2 0 1.44-.4 1.75-2.24 1.75-1.8 0-2.18-.3-2.15-1.66m-3 1.57V5.99H3.5v-.9h4.21v.9H6.1v5.22z"/>
</symbol>`,`<symbol id="file-tree-builtin-zip" viewBox="0 0 16 16">
  <path fill="currentColor" d="M4.585 2a2 2 0 0 1 1.028.285l1.788 1.072a1 1 0 0 0 .514.143H12A2 2 0 0 1 13.935 5H0V4a2 2 0 0 1 2-2z" class="bg" opacity=".5"/>
  <path fill="currentColor" fill-rule="evenodd" d="M14 12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-1.25h1v-1H0V6h14zM9.9 8.25c-.883 0-1.9.5-1.9.5H7v1h1v1s1.017.5 1.9.5c.884 0 1.6-.672 1.6-1.5s-.716-1.5-1.6-1.5M2 9.75v1h1v-1zm2 0v1h1v-1zm2 0v1h1v-1zm-5-1v1h1v-1zm2 0v1h1v-1zm2 0v1h1v-1z" class="fg" clip-rule="evenodd"/>
</symbol>`],AX=[`<symbol id="file-tree-builtin-astro" viewBox="0 0 16 16">
  <path fill="currentColor" d="M6.08 13.92c-.63-.57-.81-1.79-.55-2.67.45.56 1.08.73 1.73.83 1 .15 1.99.1 2.92-.37l.32-.19q.13.38.08.78a2.1 2.1 0 0 1-.9 1.5q-.3.24-.61.43c-.64.44-.81.95-.57 1.69l.02.08a1.7 1.7 0 0 1-.74-.64 2 2 0 0 1-.3-.98q0-.27-.02-.52-.07-.61-.61-.62a.7.7 0 0 0-.75.6z" class="bg" opacity=".6"/>
  <path fill="currentColor" d="M2.5 11.1s1.86-.9 3.72-.9l1.4-4.39c.05-.21.2-.36.38-.36s.33.15.38.36l1.4 4.38c2.2 0 3.72.92 3.72.92l-3.16-8.69q-.13-.4-.45-.42H6.11q-.3.02-.45.42z" class="fg"/>
</symbol>`,`<symbol id="file-tree-builtin-babel" viewBox="0 0 16 16">
  <path fill="currentColor" fill-rule="evenodd" d="M9.49.5q1.92.05 2.66.54 1.27.6 1.35 1.52v.23a4 4 0 0 1-.53 1.9l-1.38 1.24q-.74.38-.72.63c.77.82 1.33 1.29.85 2.42q-.47 1.1-2.04 2.28c-.5.32-1.88 1.35-2.96 1.86-1.64.77-3.1 1.4-4.65 1.89-.51.16-1.5.16-1.5.16L.5 15A76 76 0 0 0 5.76 3.49q-.1-.08-.1-.2.1 0 .32-.35l-.03-.09q-1.17.39-2.38 1.3l-.13.03q0-.1-.21-.16-.46.31-.82.7l-.13-.19.16-.06-.03-.16-.34.29L2 4.5q.36-.48.72-.54l.04-.1V3.8q.16 0 .15-.06l.13-.06a6 6 0 0 0 1.13-.9v-.03H4.1l-.12.07q0-.1-.1-.1l-.15.07-.04-.1q.93-.52 1.63-1.05Q7.89.65 9.5.5M8.46 7.83l-.32.04c-1.31.54-2.31.82-2.91.88a71 71 0 0 0-2.2 4.54h.07q.58-.04 3.04-1.42.13 0 1.66-1.05L9.18 9.7v.03q.45-.2.81-1.3v-.2q-.5-.46-1.53-.4m.28-5.75c-.5.1-.75.19-.72.38l-1.16 2.6q-.17.1-.34.95-.3.48-.25.77v.1l.22.05A15 15 0 0 1 8.86 6c1.1-.71 2.12-1.38 2.8-2.54q.24-.33.21-.54-.02-.33-.4-.54c-.54 0-1.07-.34-1.63-.28l-.94-.03z" clip-rule="evenodd"/>
</symbol>`,`<symbol id="file-tree-builtin-biome" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8 2 4.88 7.35a7 7 0 0 1 3.7-.13l1.04.25-.99 4.16-1.05-.25a2.7 2.7 0 0 0-3.07 1.45l-.98-.47a4 4 0 0 1 1.07-1.31 3.8 3.8 0 0 1 3.23-.71l.5-2.08a6 6 0 0 0-5.07 1.12A5.9 5.9 0 0 0 1 14h14z"/>
</symbol>`,`<symbol id="file-tree-builtin-bootstrap" viewBox="0 0 16 16">
  <path fill="currentColor" fill-rule="evenodd" d="M11.72 1.5A2.5 2.5 0 0 1 14.2 4q.02 1.08.3 2.09c.22.73.56 1.24 1.08 1.45.22.08.4.27.4.5s-.18.43-.4.51q-.76.34-1.08 1.45c-.2.65-.27 1.32-.3 2a2.5 2.5 0 0 1-2.48 2.5H4.25A2.6 2.6 0 0 1 1.7 12c-.04-.85-.1-1.68-.22-2.04C1.26 9.23.92 8.7.4 8.5.18 8.42 0 8.23 0 8s.18-.42.4-.5q.77-.35 1.09-1.46c.1-.36.17-1.19.2-2.04a2.6 2.6 0 0 1 2.56-2.5z" class="bg" clip-rule="evenodd" opacity=".2"/>
  <path fill="currentColor" fill-rule="evenodd" d="M8.47 4.54c1.23 0 2.04.68 2.04 1.73 0 .73-.55 1.39-1.24 1.5v.04c.94.1 1.58.77 1.58 1.7 0 1.2-.9 1.95-2.37 1.95H5.97a.3.3 0 0 1-.2-.08.3.3 0 0 1-.08-.2V4.82a.3.3 0 0 1 .08-.2.3.3 0 0 1 .2-.08zm-1.7 6.04h1.49q1.47-.01 1.49-1.15Q9.74 8.31 8.2 8.3H6.77zm0-5.16v2.06h1.21c.93 0 1.45-.38 1.45-1.06 0-.65-.44-1-1.22-1z" class="fg" clip-rule="evenodd"/>
</symbol>`,`<symbol id="file-tree-builtin-browserslist" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8.88 6.96c0 3.82 3.72 4.7 5.7 3.74-.23.9-1.04 1.67-2.35 1.93-.02.4.42 1.28.82 1.63-.9.35-1.94-.12-2.51-.48a5 5 0 0 0-.32 1.87c-.68 0-1.57-1-1.8-1.37-.3.18-.85 1.15-.96 1.72a2.4 2.4 0 0 1-.81-.86 2.4 2.4 0 0 1-.3-1.15c-.38.27-1.48.95-1.99 1.18-.25-.58-.15-1.3 0-2.06-.21.12-1.8.27-2.43.12.32-.36.75-1.19.94-1.57A4.5 4.5 0 0 1 .44 10.6c.48-.22.97-.53 1.49-1.06C1.26 9.17.24 8.64 0 7.7a6 6 0 0 0 1.79-.32C1.28 7.08.44 6.15.6 5.01c.42.21 1.3.37 1.73.3a3.4 3.4 0 0 1-.25-2.75 5 5 0 0 0 1.48 1c-.08-.8.3-2.31.8-2.71.2.46.73 1.21 1.08 1.4.09-.61.87-2.06 1.57-2.25 0 .5.27 1.4.5 1.67.51-.54 2.25-1.44 3.64-1.13-.43.45-.75.61-.86.98 1.05 0 2.78.34 4.27 1.93-2.34-.89-5.69.56-5.69 3.5" class="bg" opacity=".5"/>
  <path fill="currentColor" d="M11.21 3.59a4.1 4.1 0 0 0 2.47 2.89c.24-.22.61-.38.95-.19.76.44.2 1.26-.34 1.66l-.07.06a13 13 0 0 1-4.49 1.61l-.3-.43a10.5 10.5 0 0 0 4.13-1.31 1 1 0 0 0 .23-.25.5.5 0 0 0-.21-.69l-.15-.06a4.5 4.5 0 0 1-1.77-1.31 4.5 4.5 0 0 1-.88-1.77q.2-.12.43-.21"/>
  <path fill="currentColor" d="M10.36 5.18a.4.4 0 0 0-.03.38c.09.2.3.3.46.23s.24-.3.15-.5l-.01-.02q.23.13.34.39a.83.83 0 0 1-.43 1.08.8.8 0 0 1-1.08-.43.83.83 0 0 1 .6-1.13"/>
</symbol>`,`<symbol id="file-tree-builtin-bun" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8 14c3.87 0 7-2.46 7-5.49 0-1.88-1.2-3.53-3.04-4.52q-1.1-.61-1.84-1.07C9.2 2.35 8.64 2 8 2s-1.36.45-2.31 1.03A29 29 0 0 1 4.04 4C2.2 4.98 1 6.63 1 8.51 1 11.54 4.13 14 8 14M7.18 3.88q.3-.66.3-1.37c0-.08.11-.1.13-.01.38 1.57-.53 2.35-1.2 2.61-.08.03-.12-.07-.06-.12a3 3 0 0 0 .83-1.12m1.2-.05a3 3 0 0 0-.45-1.3V2.5c-.04-.07.05-.15.1-.1 1.15 1.2.77 2.3.33 2.87-.05.05-.13 0-.11-.08q.21-.67.13-1.37m1.04-.32a3 3 0 0 0-.94-1.02v-.01c-.06-.05-.01-.16.07-.12 1.51.61 1.61 1.8 1.43 2.5l-.03.03a.07.07 0 0 1-.1-.06 3 3 0 0 0-.43-1.32m-2.97.32c-.36.3-.74.43-1.2.56q-.11 0-.1-.1a3.5 3.5 0 0 0 1.76-1.57s.09-.07.1.04c0 .18-.2.76-.56 1.07m2.89 6.36q-.13.52-.55.88a1.3 1.3 0 0 1-.75.35 1.3 1.3 0 0 1-.77-.35 1.7 1.7 0 0 1-.54-.88.13.13 0 0 1 .15-.15h2.31a.14.14 0 0 1 .15.15M6.15 8.95a1.1 1.1 0 0 1-1.39-.14A1.1 1.1 0 0 1 5.12 7a1.1 1.1 0 0 1 1.2.25 1.1 1.1 0 0 1-.17 1.69m4.96 0a1.1 1.1 0 0 1-1.4-.14 1.1 1.1 0 0 1 .37-1.8 1.1 1.1 0 0 1 1.2.25 1.1 1.1 0 0 1 .24 1.2 1 1 0 0 1-.41.5"/>
</symbol>`,`<symbol id="file-tree-builtin-claude" viewBox="0 0 16 16">
  <path fill="currentColor" d="M3.75 10.31 6.5 8.77l.04-.14-.04-.07h-.14l-.46-.03-1.57-.04-1.38-.07-1.33-.07-.34-.07L1 7.86l.03-.21.28-.18.4.03.89.07 1.33.08.97.06 1.43.16h.22l.03-.1-.07-.05-.06-.06-1.39-.92-1.48-.98-.79-.57-.42-.28-.2-.28-.1-.6.39-.41.52.04.12.03.52.4 1.12.86L6.2 6.04l.2.17.09-.06.01-.04-.1-.15-.76-1.46-.85-1.46-.37-.6-.1-.36a1 1 0 0 1-.06-.42l.42-.59.25-.07.6.08.22.2.36.84.58 1.3.9 1.77.29.53.14.47.04.14h.1v-.07l.07-1 .14-1.22.14-1.57.04-.45.23-.53.42-.28.36.15.28.41-.04.25-.16 1.08-.36 1.7-.21 1.14h.12l.14-.15.58-.76.97-1.2.42-.5.5-.51.32-.25h.6l.44.66-.2.68-.61.79-.52.65-.74 1-.45.8.04.05h.1l1.68-.36.9-.16 1.06-.18.5.23.05.22-.2.48-1.15.28-1.34.28-2 .46-.04.01.03.04.9.09.4.03h.94l1.77.14.46.28.27.37-.04.28-.72.37-.95-.23-2.24-.53-.76-.18h-.11v.06l.64.63L12 10.86l1.48 1.35.07.34-.18.28-.2-.03-1.29-.98-.5-.42-1.12-.95h-.07v.1l.25.38 1.37 2.05.07.63-.1.2-.36.14-.38-.08-.8-1.12-.85-1.26-.66-1.15-.07.05-.4 4.23-.19.21-.42.17-.35-.28-.2-.42.2-.87.23-1.12.18-.9.17-1.1.1-.36v-.03h-.1l-.84 1.16-1.27 1.72-1 1.07-.24.1-.42-.22.04-.39.22-.32 1.4-1.8.84-1.1.57-.64-.02-.07h-.04l-3.7 2.4-.66.09-.28-.28.03-.42.14-.14 1.12-.77z"/>
</symbol>`,`<symbol id="file-tree-builtin-docker" viewBox="0 0 16 16">
  <path fill="currentColor" d="M15.85 6.54c-.05-.04-.45-.36-1.31-.36q-.34 0-.68.06a2.7 2.7 0 0 0-1.14-1.79l-.23-.14-.15.23a3 3 0 0 0-.4 1q-.24 1.01.26 1.84c-.4.24-1.03.3-1.17.3H.5a.5.5 0 0 0-.5.52q-.01 1.46.46 2.83.55 1.5 1.6 2.18c.79.5 2.08.79 3.54.79q.96 0 1.94-.18a8 8 0 0 0 2.55-.97 7 7 0 0 0 1.73-1.5 10 10 0 0 0 1.7-3.06h.15a2.4 2.4 0 0 0 1.8-.7 2 2 0 0 0 .47-.74l.06-.2z"/>
  <path fill="currentColor" d="M1.48 7.36h1.4a.14.14 0 0 0 .14-.13V5.91q-.01-.12-.13-.14H1.48a.13.13 0 0 0-.13.14v1.32q.02.13.13.13m1.94 0h1.41a.14.14 0 0 0 .13-.13V5.91q-.01-.12-.13-.14h-1.4a.13.13 0 0 0-.13.14v1.32q0 .13.12.13m1.98 0h1.4q.13 0 .14-.13V5.91a.13.13 0 0 0-.14-.14H5.4q-.1.01-.12.14v1.32q0 .13.12.13m1.95 0h1.42q.1 0 .12-.13V5.91q0-.12-.12-.14H7.35q-.1.01-.12.14v1.32q.01.13.12.13M3.42 5.5h1.41c.07 0 .13-.08.13-.15V4.03a.13.13 0 0 0-.13-.14h-1.4q-.12 0-.13.14v1.31q0 .13.12.15m1.98 0h1.4c.08 0 .14-.08.14-.15V4.03q0-.13-.14-.14H5.4q-.1 0-.12.14v1.31q0 .13.12.15m1.95 0h1.42c.06 0 .12-.08.12-.15V4.03q-.01-.13-.12-.14H7.35q-.1 0-.12.14v1.31q.01.13.12.15m0-1.9h1.42q.1-.02.12-.14v-1.3Q8.88 2 8.77 2H7.35q-.1 0-.12.14v1.3q.01.13.12.14m1.97 3.78h1.4a.13.13 0 0 0 .14-.13V5.91q-.01-.12-.13-.14H9.32q-.1.01-.12.14v1.32q.01.13.12.13" opacity=".5"/>
</symbol>`,`<symbol id="file-tree-builtin-eslint" viewBox="0 0 16 16">
  <path fill="currentColor" d="M11.16 6.1 8.12 4.35a.3.3 0 0 0-.24 0L4.84 6.1a.3.3 0 0 0-.12.2v3.5q0 .14.12.22l3.04 1.74q.12.08.24 0l3.04-1.74a.2.2 0 0 0 .13-.22V6.3a.3.3 0 0 0-.13-.2" opacity=".5"/>
  <path fill="currentColor" d="m.1 7.69 3.63-6.3A.8.8 0 0 1 4.37 1h7.26c.26 0 .5.17.64.4l3.63 6.27a.8.8 0 0 1 0 .75l-3.63 6.24a.7.7 0 0 1-.64.34H4.37a.7.7 0 0 1-.64-.34L.1 8.41a.7.7 0 0 1 0-.72m3 3.02q.01.15.14.23l4.63 2.66q.13.06.26 0l4.63-2.66a.3.3 0 0 0 .14-.23V5.4a.3.3 0 0 0-.14-.23L8.13 2.52a.3.3 0 0 0-.26 0L3.24 5.17a.3.3 0 0 0-.14.23z"/>
</symbol>`,`<symbol id="file-tree-builtin-graphql" viewBox="0 0 16 16">
  <path fill="currentColor" fill-rule="evenodd" d="M8 1a1.25 1.25 0 0 1 1.18 1.65l2.8 1.61q.33-.25.77-.26a1.25 1.25 0 0 1 .48 2.4v3.2a1.25 1.25 0 1 1-1.25 2.13l-2.8 1.62A1.25 1.25 0 0 1 8 15a1.25 1.25 0 0 1-1.18-1.65l-2.8-1.62q-.33.26-.77.27a1.25 1.25 0 0 1-.48-2.4V6.4a1.25 1.25 0 1 1 1.25-2.14l2.8-1.61A1.25 1.25 0 0 1 8 1M4.44 11.14l-.06.13 2.75 1.58a1.25 1.25 0 0 1 1.74 0l2.74-1.58-.05-.13zm3.89-7.68a1.3 1.3 0 0 1-.66 0L4.03 9.77q.37.3.45.78h7.04q.08-.48.45-.78zM4.38 4.73a1.24 1.24 0 0 1-1.02 1.76v3.02l.13.01 3.67-6.35-.03-.02zm4.46-1.56 3.67 6.35.13-.01V6.49a1.25 1.25 0 0 1-1.03-1.76L8.87 3.15z" clip-rule="evenodd"/>
</symbol>`,`<symbol id="file-tree-builtin-nextjs" viewBox="0 0 16 16">
  <defs>
  <linearGradient id="a" x1="4.522" x2="14" y1="3.943" y2="16" gradientUnits="userSpaceOnUse">
  <stop stop-color="currentColor"/>
  <stop offset="1" stop-color="currentColor" stop-opacity="0"/>
  </linearGradient>
  </defs>
  <path fill="currentColor" d="M3 2h1.522v9.09H3z"/>
  <path fill="url(#a)" d="M4.903 2 15 15.075q-.565.5-1.195.925L4.522 3.943z"/>
  <path fill="currentColor" d="M12.172 2h-1.508v9.094h1.508z"/>
</symbol>`,`<symbol id="file-tree-builtin-npm" viewBox="0 0 16 16">
  <path fill="currentColor" d="M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1z" class="vector" opacity=".2"/>
  <path fill="currentColor" d="M10.5 13H13V3H3v10h5V5.5h2.5z"/>
</symbol>`,`<symbol id="file-tree-builtin-oxc" viewBox="0 0 16 16">
  <path fill="currentColor" d="M9.5 1a.5.5 0 0 1 .5.5V3h3.5a.5.5 0 0 1 .38.83L10.5 7.69v1.44q.41.04.95-.16a4 4 0 0 0 .72-.35l.04-.03h.01a.5.5 0 0 1 .67.1l2 2.5a.5.5 0 0 1 0 .62c-.76.96-3.14 2.69-6.89 2.69s-6.13-1.73-6.89-2.69a.5.5 0 0 1 0-.62l2-2.5a.5.5 0 0 1 .67-.1l.05.03.16.09q.22.13.56.26.54.2.95.16V7.69L2.12 3.83A.5.5 0 0 1 2.5 3H6V1.5a.5.5 0 0 1 .5-.5zM7 3.5a.5.5 0 0 1-.5.5H3.6l2.78 3.17a.5.5 0 0 1 .12.33v2a.5.5 0 0 1-.28.45c-.7.35-1.5.15-2.02-.05a5 5 0 0 1-.58-.26l-1.46 1.84c.82.78 2.8 2.02 5.84 2.02s5.02-1.24 5.84-2.02l-1.46-1.83a5 5 0 0 1-.58.26c-.52.2-1.33.39-2.02.04a.5.5 0 0 1-.28-.45v-2a.5.5 0 0 1 .12-.33L12.4 4H9.5a.5.5 0 0 1-.5-.5V2H7z"/>
</symbol>`,`<symbol id="file-tree-builtin-postcss" viewBox="0 0 16 16">
  <path fill="currentColor" d="M14.5 8a6.5 6.5 0 0 0-5.9-6.47l5.42 8.93A7 7 0 0 0 14.5 8M2.88 12A6.5 6.5 0 0 0 8 14.5c2.08 0 3.93-.98 5.12-2.5zm8.62-1h1.68L11.5 8.24zm-1-.55a4 4 0 0 1-.7.55h.7zM8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5M5.5 11h.7a4 4 0 0 1-.7-.55zm-2.68 0H4.5V8.24zm3.76-6.2A4 4 0 0 1 8 4.5q.76 0 1.42.3L8 2.46zM1.5 8q0 1.31.48 2.46L7.4 1.53A6.5 6.5 0 0 0 1.5 8m14 0a7.5 7.5 0 0 1-.99 3.72l-.01.03-.02.03A7.5 7.5 0 0 1 8 15.5a7.5 7.5 0 0 1-6.5-3.75l-.01-.03A7.5 7.5 0 1 1 15.5 8"/>
</symbol>`,`<symbol id="file-tree-builtin-prettier" viewBox="0 0 16 16">
  <path fill="currentColor" d="M6 12v1H4.93v-1zm1-2v1H2v-1zm6-4v1h-3V6zm-1-4v1H9V2z"/>
  <path fill="currentColor" d="M11.5 10v1H8v-1zM5 6v1H2V6zm5-2v1H9V4z" opacity=".8"/>
  <path fill="currentColor" d="M6 14v1H2v-1zm-.5-6v1H2V8zM13 4v1h-3V4zM4.93 2v1H2V2z" opacity=".6"/>
  <path fill="currentColor" d="M4.93 12v1H2v-1zM13 8v1H9V8zM5.5 4v1H2V4zM9 2v1H4.93V2z" opacity=".4"/>
</symbol>`,`<symbol id="file-tree-builtin-react" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8 6.65c.73 0 1.31.6 1.31 1.35S8.73 9.35 8 9.35 6.69 8.75 6.69 8 7.27 6.65 8 6.65"/>
  <path fill="currentColor" fill-rule="evenodd" d="M8 2.55c1.3-.99 2.59-1.34 3.5-.8.92.55 1.27 1.87 1.08 3.53C14.06 5.94 15 6.9 15 8s-.94 2.06-2.42 2.72c.19 1.65-.16 2.98-1.08 3.52-.91.55-2.2.2-3.5-.8-1.3 1-2.58 1.35-3.5.8-.91-.54-1.27-1.87-1.08-3.52C1.94 10.06 1 9.1 1 8s.94-2.06 2.42-2.72c-.19-1.66.17-2.98 1.08-3.52s2.2-.2 3.5.8M4.26 11.2c-.08 1.34.28 2.03.68 2.26s1.15.22 2.25-.52l.11-.09a12 12 0 0 1-1.24-1.39 11 11 0 0 1-1.8-.41zm7.47-.15q-.83.27-1.79.41-.6.8-1.24 1.4l.11.08c1.1.74 1.86.76 2.25.52.4-.23.76-.92.68-2.26zm-3.04.54a14 14 0 0 1-1.38 0q.34.38.69.7.35-.32.7-.7M8 5.29q-.76 0-1.47.1A13 13 0 0 0 5.07 8a14 14 0 0 0 1.46 2.62 13 13 0 0 0 2.94 0A13 13 0 0 0 10.93 8a14 14 0 0 0-1.46-2.62A13 13 0 0 0 8 5.3M4.64 9.18q-.15.5-.25.96.44.16.94.27a15 15 0 0 1-.7-1.23m6.73 0a15 15 0 0 1-.7 1.23q.5-.11.95-.27a10 10 0 0 0-.25-.96M3.44 6.26C2.27 6.86 1.87 7.53 1.87 8s.4 1.14 1.57 1.74l.13.07q.18-.88.55-1.81a12 12 0 0 1-.55-1.8q-.07.02-.13.06m8.99-.07A12 12 0 0 1 11.88 8q.36.94.55 1.8l.13-.06c1.17-.6 1.56-1.27 1.56-1.74s-.39-1.14-1.56-1.74zm-7.1-.6q-.5.11-.94.27.1.46.25.96a15 15 0 0 1 .69-1.23m5.34 0a15 15 0 0 1 .7 1.23q.14-.5.24-.96-.44-.15-.94-.27M7.18 3.06c-1.09-.74-1.85-.76-2.24-.52s-.76.92-.69 2.26l.01.15a11 11 0 0 1 1.8-.41q.6-.8 1.24-1.4zm3.88-.52c-.4-.24-1.15-.22-2.25.52l-.12.08q.65.6 1.25 1.4.96.15 1.8.41v-.14c.08-1.35-.28-2.04-.68-2.27M8 3.7a10 10 0 0 0-.7.7 14 14 0 0 1 1.4 0 10 10 0 0 0-.7-.7" clip-rule="evenodd"/>
</symbol>`,`<symbol id="file-tree-builtin-sass" viewBox="0 0 16 16">
  <path fill="currentColor" fill-rule="evenodd" d="M8.08 1.44c2.41-.91 4.96-.37 5.35 1.27.39 1.62-.92 3.56-2.6 4.25a5 5 0 0 1-3.26.35c-.58-.2-.92-.62-1-.85-.03-.09-.09-.24 0-.3.05-.03.08-.02.22.15s.7.6 1.75.48c2.78-.34 4.45-2.64 3.92-3.88-.37-.87-2.5-1.26-5.18.16C4.03 4.81 3.85 6.24 3.82 6.8c-.08 1.5 1.73 2.28 2.7 3.4q.04.03.07.08c.3-.12.7-.19 1.35-.2 1.58-.03 2.47 1.08 2.43 2.08-.03.78-.7 1.1-.82 1.13-.1.01-.14.02-.15-.06q-.03-.06.13-.15c.16-.09.42-.3.48-.72.05-.43-.24-1.44-1.76-1.63a3 3 0 0 0-1.33.08c.27.62.32 1.87-.29 2.83-.63 1-1.8 1.61-2.93 1.27-.37-.1-.93-.92-.45-2.05.46-1.07 2.4-2.12 2.66-2.26-.9-.83-3.08-1.95-3.4-3.65-.08-.49.13-1.65 1.46-2.98a12 12 0 0 1 4.11-2.52m-1.88 9.7c-.01.01-.9.47-1.52 1.17-.59.66-.75 1.48-.43 1.69.3.18 1-.04 1.51-.62a3 3 0 0 0 .5-.9q.2-.64.02-1.39z" clip-rule="evenodd"/>
</symbol>`,`<symbol id="file-tree-builtin-stylelint" viewBox="0 0 16 16">
  <path fill="currentColor" d="M4 3v3.5l1.5-1L7 15 .5 6l1-1.5L0 3l2.5-2h1zm12 0-1.5 1.5 1 1.5L9 15l1.5-9.5 1.5 1V3l.5-2h1zm-8 8.5a.5.5 0 1 1 0 1 .5.5 0 0 1 0-1m0-3a.5.5 0 1 1 0 1 .5.5 0 0 1 0-1m0-3a.5.5 0 1 1 0 1 .5.5 0 0 1 0-1"/>
  <path fill="currentColor" d="M6.5 2.5V4l-2 1.5v-4zm5 3L9.5 4V2.5l2-1zM9 4H7V2.5h2z"/>
</symbol>`,`<symbol id="file-tree-builtin-svelte" viewBox="0 0 16 16">
  <path fill="currentColor" d="m3.98 3.7 3.36-2.08a4.5 4.5 0 0 1 5.9 1.23 4 4 0 0 1 .7 3.02q-.16.75-.58 1.4c.42.77.56 1.66.4 2.52a3.7 3.7 0 0 1-1.57 2.4l-.17.1-3.36 2.09a4.5 4.5 0 0 1-5.9-1.23 4 4 0 0 1-.66-1.44 4 4 0 0 1-.04-1.58 4 4 0 0 1 .58-1.4 4 4 0 0 1-.4-2.52 3.7 3.7 0 0 1 1.57-2.4zl3.36-2.08zm7.87 0a2.7 2.7 0 0 0-1.26-.95 2.7 2.7 0 0 0-1.6-.07 3 3 0 0 0-.52.2l-.16.09-3.36 2.08a2 2 0 0 0-.69.64 2 2 0 0 0-.36.86 2.3 2.3 0 0 0 .42 1.81A2.7 2.7 0 0 0 7.18 9.4q.28-.06.53-.2l.16-.09 1.28-.79.2-.09a.8.8 0 0 1 .87.31.7.7 0 0 1 .13.55.7.7 0 0 1-.24.4l-.08.05-3.36 2.08-.2.09a1 1 0 0 1-.49-.02 1 1 0 0 1-.38-.3 1 1 0 0 1-.13-.37v-.1l.01-.13-.13-.03a4 4 0 0 1-1.1-.5l-.2-.14-.18-.12-.07.18-.08.3a2.3 2.3 0 0 0 .43 1.82q.45.64 1.19.93.73.28 1.51.14l.16-.04q.27-.07.52-.2l.16-.09 3.36-2.08q.4-.25.69-.64.27-.4.36-.86a2.3 2.3 0 0 0-.42-1.82 2.7 2.7 0 0 0-1.27-.95 2.7 2.7 0 0 0-1.6-.08q-.27.07-.52.2l-.16.1-1.28.79-.2.09a1 1 0 0 1-.49-.03 1 1 0 0 1-.38-.29.7.7 0 0 1-.13-.54.7.7 0 0 1 .24-.4l.08-.06L9.33 4.4l.2-.1a.8.8 0 0 1 .87.32 1 1 0 0 1 .13.38v.22l.11.04q.6.18 1.12.5l.2.14.17.12.06-.19.08-.3a2.3 2.3 0 0 0-.42-1.81z"/>
</symbol>`,`<symbol id="file-tree-builtin-svg" viewBox="0 0 16 16">
  <path fill="currentColor" d="M5 7a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2z"/>
  <path fill="currentColor" d="M6 1a5 5 0 0 1 4.58 3H7a3 3 0 0 0-3 3v3.58A5 5 0 0 1 6 1" opacity=".5"/>
</symbol>`,`<symbol id="file-tree-builtin-svgo" viewBox="0 0 16 16">
  <path fill="currentColor" d="M9.43 4.8A.6.6 0 1 1 9.19 6l-.56.96a1.2 1.2 0 0 1 .32 1.58l.7.53a.89.89 0 1 1-.17.22l-.7-.52a1.2 1.2 0 0 1-1.4.25l-.56.87a.75.75 0 1 1-.57-.2 1 1 0 0 1 .32.05l.56-.87a1.2 1.2 0 0 1-.4-1.24l-1.2-.47a.56.56 0 1 1 .1-.28v.02l1.2.47a1.2 1.2 0 0 1 1.56-.55l.56-.97a.6.6 0 0 1-.15-.64.6.6 0 0 1 .63-.4"/>
  <path fill="currentColor" fill-rule="evenodd" d="M9.17 1q.16.63.27 1.26a6 6 0 0 1 1.61.67q.52-.38 1.08-.71l1.65 1.64q-.32.56-.68 1.05.48.78.72 1.67.6.09 1.18.25v2.32q-.55.15-1.11.24a6 6 0 0 1-.7 1.82q.31.44.59.91l-1.65 1.65-.85-.55a6 6 0 0 1-1.9.83q-.08.47-.2.95H6.84q-.12-.46-.2-.93a6 6 0 0 1-1.96-.81q-.39.27-.8.51l-1.65-1.65q.25-.43.53-.84a6 6 0 0 1-.75-1.9L1 9.16V6.83q.54-.14 1.09-.24a6 6 0 0 1 .77-1.74q-.33-.47-.63-.98l1.65-1.65q.54.32 1.03.68a6 6 0 0 1 1.66-.66q.1-.61.26-1.24zM7.96 3.73a4 4 0 0 0-1.74.36 4.5 4.5 0 0 0-2.3 2.3 4.4 4.4 0 0 0-.1 3.29l.03.06a4.4 4.4 0 0 0 2.4 2.47 4.4 4.4 0 0 0 3.48-.02l.03-.02a4.4 4.4 0 0 0 2.3-2.42l.06-.14a4.4 4.4 0 0 0-.2-3.4 4.4 4.4 0 0 0-2.13-2.07L9.47 4a4 4 0 0 0-1.51-.27" clip-rule="evenodd"/>
</symbol>`,`<symbol id="file-tree-builtin-tailwind" viewBox="0 0 16 16">
  <path fill="currentColor" fill-rule="evenodd" d="M8 4Q5.2 4 4.5 6.67q1.05-1.34 2.45-1c.53.12.91.5 1.33.9C8.98 7.23 9.77 8 11.5 8q2.8 0 3.5-2.67-1.05 1.34-2.45 1c-.53-.12-.91-.5-1.33-.9C10.52 4.77 9.73 4 8 4M4.5 8Q1.7 8 1 10.67q1.05-1.34 2.45-1c.53.12.91.5 1.33.9C5.48 11.23 6.26 12 8 12q2.8 0 3.5-2.67-1.05 1.34-2.45 1c-.53-.12-.91-.5-1.33-.9C7.02 8.77 6.24 8 4.5 8" clip-rule="evenodd"/>
</symbol>`,`<symbol id="file-tree-builtin-terraform" viewBox="0 0 16 16">
  <path fill="currentColor" d="M1 0v5.05l4.35 2.53V2.53zm9.18 5.34L5.83 2.82v5.05l4.35 2.53zm.47 5.06V5.34L15 2.82v5.05zm-.48 5.6-4.35-2.53V8.42l4.35 2.53z"/>
</symbol>`,`<symbol id="file-tree-builtin-vite" viewBox="0 0 16 16">
  <path fill="currentColor" d="M8.57 14.87c-.18.26-.55.11-.55-.22v-3.18l-.05-.27-.13-.22-.2-.15-.24-.06H4.29c-.26 0-.4-.32-.26-.55L6.08 7c.3-.46 0-1.1-.5-1.1H1.8c-.25 0-.4-.32-.25-.56l2.65-4.2A.3.3 0 0 1 4.46 1h7.9c.26 0 .4.32.26.55l-2.05 3.23c-.29.46 0 1.1.5 1.1h3.12c.26 0 .4.34.24.57z"/>
</symbol>`,`<symbol id="file-tree-builtin-vscode" viewBox="0 0 16 16">
  <path fill="currentColor" d="m5.11 9.68-2.4 1.84a.6.6 0 0 1-.75-.04l-.77-.7a.6.6 0 0 1 0-.87L3.28 8zm5.52-8.42a.51.51 0 0 1 .87.36V4.8L7.32 8 5.1 6.32z" opacity=".75"/>
  <path fill="currentColor" d="M11.1 14.99h.03zM1.96 4.52a.6.6 0 0 1 .75-.04l8.8 6.71v3.19a.51.51 0 0 1-.88.36L1.19 6.1a.6.6 0 0 1 0-.87z" opacity=".65"/>
  <path fill="currentColor" d="M11.62 14.91a.9.9 0 0 1-1-.17.51.51 0 0 0 .88-.36V1.62a.51.51 0 0 0-.87-.36.9.9 0 0 1 1-.17l2.87 1.39a.9.9 0 0 1 .5.8v9.44a.9.9 0 0 1-.5.8z"/>
</symbol>`,`<symbol id="file-tree-builtin-vue" viewBox="0 0 16 16">
  <path fill="currentColor" d="M9.62 2.25 8 5.02 6.38 2.25H1l7 12 7-12z" opacity=".5"/>
  <path fill="currentColor" d="M9.54 2.25 8 4.95l-1.54-2.7H4l4 7 4-7z"/>
</symbol>`,`<symbol id="file-tree-builtin-wasm" viewBox="0 0 16 16">
  <path fill="currentColor" d="M13 1a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h3a2 2 0 1 0 4 0z" class="subtract" opacity=".2"/>
  <path fill="currentColor" d="M4.64 11.4h.02l.8-3.4h.91l.73 3.45L7.88 8h.96l-1.25 5h-.97L5.9 9.6 5.1 13h-1L3 8h.98z"/>
  <path fill="currentColor" fill-rule="evenodd" d="M13 13h-1.02l-.33-1.11H9.9L9.64 13h-.97l1.26-5h1.54zm-2.49-3.77-.42 1.84h1.32l-.49-1.84z" clip-rule="evenodd"/>
</symbol>`,`<symbol id="file-tree-builtin-webpack" viewBox="0 0 16 16">
  <path fill="currentColor" d="M14.1 11.79 8.26 15v-2.5l3.64-1.94zm.4-.35V4.73l-2.14 1.2v4.3zm-12.6.35L7.74 15v-2.5L4.1 10.56zm-.4-.35V4.73l2.14 1.2v4.3zm.25-7.15 6-3.29v2.42L3.9 5.47l-.03.01zm12.5 0L8.25 1v2.42l3.85 2.05.03.01z" class="bg" opacity=".4"/>
  <path fill="currentColor" d="m7.74 11.93-3.59-1.92v-3.8l3.6 2.02zm.52 0 3.59-1.92v-3.8l-3.6 2.02zM4.4 5.77 8 3.85l3.6 1.93L8 7.8z" class="fg"/>
</symbol>`,`<symbol id="file-tree-builtin-yml" viewBox="0 0 16 16">
  <path fill="currentColor" d="M7.5 2A1.5 1.5 0 0 1 9 3.5v3A1.5 1.5 0 0 1 7.5 8h-2v2A1.5 1.5 0 0 0 7 11.5v-1A1.5 1.5 0 0 1 8.5 9h5a1.5 1.5 0 0 1 1.5 1.5v3a1.5 1.5 0 0 1-1.5 1.5h-5A1.5 1.5 0 0 1 7 13.5v-1A2.5 2.5 0 0 1 4.5 10V8h-2A1.5 1.5 0 0 1 1 6.5v-3A1.5 1.5 0 0 1 2.5 2zm1 8a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h5a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5zm-6-7a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h5a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5z"/>
</symbol>`,`<symbol id="file-tree-builtin-zig" viewBox="0 0 16 16">
  <path fill="currentColor" d="m14.73 1.5-7.29 8.82h4.17l-1.73 2.04H5.76L1.27 14.5l7.3-8.91H4.39l1.73-2.05h4.12z"/>
  <path fill="currentColor" d="M5.21 3.54 3.56 5.6h-.55v4.73h.83L2.1 12.36H1V3.54zm9.79 0v8.82h-4.3l1.74-2.04h.55V5.68h-.83l1.74-2.14z"/>
</symbol>`];function K9(X,Q){if(Q.length===0)return X;return X.replace("</svg>",`
  ${Q.join(`
  `)}
</svg>`)}var U9=K9(`<svg data-icon-sprite aria-hidden="true" width="0" height="0">
  <symbol id="file-tree-icon-chevron" viewBox="0 0 16 16">
    <path d="M3.47 5.47a.75.75 0 0 1 1.06 0L8 8.94l3.47-3.47a.75.75 0 1 1 1.06 1.06l-4 4a.75.75 0 0 1-1.06 0l-4-4a.75.75 0 0 1 0-1.06" fill="currentcolor"/>
  </symbol>
  <symbol id="file-tree-icon-dot" viewBox="0 0 6 6">
    <circle cx="3" cy="3" r="3" />
  </symbol>
  <symbol id="file-tree-icon-file" viewBox="0 0 16 16">
    <path fill="currentColor" d="M8 1v3a3 3 0 0 0 3 3h3v5.5a2.5 2.5 0 0 1-2.5 2.5h-7A2.5 2.5 0 0 1 2 12.5v-9A2.5 2.5 0 0 1 4.5 1z" class="bg" opacity=".5"/>
    <path fill="currentColor" d="M9.5 1a.5.5 0 0 1 .354.146l4 4A.5.5 0 0 1 14 5.5V6h-3a2 2 0 0 1-2-2V1z" class="fg"/>
  </symbol>
  <symbol id="file-tree-icon-lock" viewBox="0 0 16 16">
    <path fill="currentcolor" d="M4 5.336V4a4 4 0 1 1 8 0v1.336c1.586.54 2 1.843 2 4.664v1c0 4.118-.883 5-5 5H7c-4.117 0-5-.883-5-5v-1c0-2.821.414-4.124 2-4.664M5.5 4v1.054Q6.166 4.998 7 5h2q.834-.002 1.5.054V4a2.5 2.5 0 0 0-5 0m-2 6v1c0 .995.055 1.692.167 2.193.107.483.246.686.35.79s.307.243.79.35c.5.112 1.198.167 2.193.167h2c.995 0 1.692-.055 2.193-.166.483-.108.686-.247.79-.35.104-.105.243-.308.35-.791.112-.5.167-1.198.167-2.193v-1c0-.995-.055-1.692-.166-2.193-.108-.483-.247-.686-.35-.79-.105-.104-.308-.243-.791-.35C10.693 6.555 9.995 6.5 9 6.5H7c-.995 0-1.692.055-2.193.167-.483.107-.686.246-.79.35s-.243.307-.35.79C3.555 8.307 3.5 9.005 3.5 10" />
  </symbol>
  <symbol id="file-tree-icon-ellipsis" viewBox="0 0 16 16">
    <path d="M5 8.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0M9.5 8.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0M14 8.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0" />
  </symbol>
</svg>`,HX),LX={minimal:`<svg data-icon-sprite aria-hidden="true" width="0" height="0">
  <symbol id="file-tree-icon-chevron" viewBox="0 0 16 16">
    <path d="M3.47 5.47a.75.75 0 0 1 1.06 0L8 8.94l3.47-3.47a.75.75 0 1 1 1.06 1.06l-4 4a.75.75 0 0 1-1.06 0l-4-4a.75.75 0 0 1 0-1.06" fill="currentcolor"/>
  </symbol>
  <symbol id="file-tree-icon-dot" viewBox="0 0 6 6">
    <circle cx="3" cy="3" r="3" />
  </symbol>
  <symbol id="file-tree-icon-file" viewBox="0 0 16 16">
    <path fill="currentColor" d="M8 1v3a3 3 0 0 0 3 3h3v5.5a2.5 2.5 0 0 1-2.5 2.5h-7A2.5 2.5 0 0 1 2 12.5v-9A2.5 2.5 0 0 1 4.5 1z" class="bg" opacity=".5"/>
    <path fill="currentColor" d="M9.5 1a.5.5 0 0 1 .354.146l4 4A.5.5 0 0 1 14 5.5V6h-3a2 2 0 0 1-2-2V1z" class="fg"/>
  </symbol>
  <symbol id="file-tree-icon-lock" viewBox="0 0 16 16">
    <path fill="currentcolor" d="M4 5.336V4a4 4 0 1 1 8 0v1.336c1.586.54 2 1.843 2 4.664v1c0 4.118-.883 5-5 5H7c-4.117 0-5-.883-5-5v-1c0-2.821.414-4.124 2-4.664M5.5 4v1.054Q6.166 4.998 7 5h2q.834-.002 1.5.054V4a2.5 2.5 0 0 0-5 0m-2 6v1c0 .995.055 1.692.167 2.193.107.483.246.686.35.79s.307.243.79.35c.5.112 1.198.167 2.193.167h2c.995 0 1.692-.055 2.193-.166.483-.108.686-.247.79-.35.104-.105.243-.308.35-.791.112-.5.167-1.198.167-2.193v-1c0-.995-.055-1.692-.166-2.193-.108-.483-.247-.686-.35-.79-.105-.104-.308-.243-.791-.35C10.693 6.555 9.995 6.5 9 6.5H7c-.995 0-1.692.055-2.193.167-.483.107-.686.246-.79.35s-.243.307-.35.79C3.555 8.307 3.5 9.005 3.5 10" />
  </symbol>
  <symbol id="file-tree-icon-ellipsis" viewBox="0 0 16 16">
    <path d="M5 8.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0M9.5 8.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0M14 8.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0" />
  </symbol>
</svg>`,standard:U9,complete:K9(U9,AX)},OX={".babelrc":"babel",".babelrc.json":"babel",".bash_profile":"bash",".bashrc":"bash",".browserslistrc":"browserslist",".dockerignore":"docker",".eslintignore":"eslint",".eslintrc":"eslint",".eslintrc.cjs":"eslint",".eslintrc.js":"eslint",".eslintrc.json":"eslint",".eslintrc.yaml":"eslint",".eslintrc.yml":"eslint",".gitattributes":"git",".gitignore":"git",".gitkeep":"git",".gitmodules":"git",".oxlintrc.json":"oxc",".postcssrc":"postcss",".postcssrc.json":"postcss",".postcssrc.yaml":"postcss",".postcssrc.yml":"postcss",".prettierignore":"prettier",".prettierrc":"prettier",".prettierrc.cjs":"prettier",".prettierrc.js":"prettier",".prettierrc.json":"prettier",".prettierrc.mjs":"prettier",".prettierrc.toml":"prettier",".prettierrc.yaml":"prettier",".prettierrc.yml":"prettier",".stylelintignore":"stylelint",".stylelintrc":"stylelint",".stylelintrc.cjs":"stylelint",".stylelintrc.js":"stylelint",".stylelintrc.json":"stylelint",".stylelintrc.mjs":"stylelint",".stylelintrc.yaml":"stylelint",".stylelintrc.yml":"stylelint",".terraform.lock.hcl":"terraform",".zprofile":"bash",".zshenv":"bash",".zshrc":"bash","babel.config.cjs":"babel","babel.config.js":"babel","babel.config.json":"babel","babel.config.mjs":"babel","biome.json":"biome","biome.jsonc":"biome","bootstrap.bundle.js":"bootstrap","bootstrap.bundle.min.js":"bootstrap","bootstrap.css":"bootstrap","bootstrap.js":"bootstrap","bootstrap.min.css":"bootstrap","bootstrap.min.js":"bootstrap","bun.lock":"bun","bun.lockb":"bun","bunfig.toml":"bun","claude.md":"claude","compose.yaml":"docker","compose.yml":"docker","docker-compose.override.yml":"docker","docker-compose.yaml":"docker","docker-compose.yml":"docker",dockerfile:"docker","eslint.config.cjs":"eslint","eslint.config.js":"eslint","eslint.config.mjs":"eslint","eslint.config.mts":"eslint","eslint.config.ts":"eslint",gemfile:"ruby","next.config.js":"nextjs","next.config.mjs":"nextjs","next.config.mts":"nextjs","next.config.ts":"nextjs","postcss.config.cjs":"postcss","postcss.config.js":"postcss","postcss.config.mjs":"postcss","postcss.config.ts":"postcss","prettier.config.cjs":"prettier","prettier.config.js":"prettier","prettier.config.mjs":"prettier",rakefile:"ruby","readme.md":"markdown","stylelint.config.cjs":"stylelint","stylelint.config.js":"stylelint","stylelint.config.mjs":"stylelint","svgo.config.cjs":"svgo","svgo.config.js":"svgo","svgo.config.mjs":"svgo","svgo.config.ts":"svgo","tailwind.config.cjs":"tailwind","tailwind.config.js":"tailwind","tailwind.config.mjs":"tailwind","tailwind.config.ts":"tailwind","vite.config.js":"vite","vite.config.mjs":"vite","vite.config.mts":"vite","vite.config.ts":"vite","webpack.config.babel.js":"webpack","webpack.config.cjs":"webpack","webpack.config.js":"webpack","webpack.config.mjs":"webpack","webpack.config.ts":"webpack"},BX={"7z":"zip",astro:"astro",AUTHORS:"text",avif:"image",bash:"bash",bmp:"image",bz2:"zip",cfg:"text",CHANGELOG:"text",cjs:"javascript","code-workspace":"vscode",conf:"text",CONTRIBUTORS:"text",csh:"bash",css:"css",csv:"table",cts:"typescript",db:"database",editorconfig:"text",env:"text","env.development":"text","env.local":"text","env.production":"text",eot:"font",erb:"ruby",fish:"bash",gemspec:"ruby",gif:"image",go:"go",gql:"graphql",graphql:"graphql",gz:"zip",htm:"html",html:"html",icns:"image",ico:"image",ini:"text",jar:"zip",jpeg:"image",jpg:"image",js:"javascript",json:"json",json5:"json",jsonc:"json",jsonl:"json",jsx:"javascript",ksh:"bash",less:"css",LICENSE:"text",log:"text",markdown:"markdown",mcp:"mcp",md:"markdown",mdx:"markdown","mdx.tsx":"markdown",mjs:"javascript",mts:"typescript",ods:"table",otf:"font",png:"image",postcss:"css",py:"python",pyi:"python",pyw:"python",pyx:"python",rake:"ruby",rar:"zip",rb:"ruby",rs:"rust",rst:"text",rtf:"text",sass:"css",scss:"css",sh:"bash",sql:"database",sqlite:"database",sqlite3:"database",styl:"css",svelte:"svelte",svg:"svg",swift:"swift",tar:"zip",tf:"terraform",tfstate:"terraform",tfvars:"terraform",tgz:"zip",tif:"image",tiff:"image",ts:"typescript",tsv:"table",tsx:"typescript",ttf:"font",txt:"text",vue:"vue",war:"zip",wasm:"wasm",wast:"wasm",wat:"wasm",webp:"image",woff:"font",woff2:"font",xhtml:"html",xls:"table",xlsx:"table",xz:"zip",yaml:"yml",yml:"yml",zig:"zig",zip:"zip",zsh:"bash"},jX={jsx:"react",sass:"sass",scss:"sass",tsx:"react"},z9=new Set(["bash","css","database","default","font","git","go","html","image","javascript","json","markdown","mcp","python","ruby","rust","swift","table","text","typescript","zip"]),_X=new Set(["complete"]);function M9(X){return LX[X==="none"?"minimal":X]}function H9(X){return`file-tree-builtin-${X}`}function A9(X){return X!=="none"&&_X.has(X)}function L9(X,Q,Z){if(X==="minimal"||X==="none")return;let Y=X==="complete",J=OX[Q.toLowerCase()];if(J!=null){if(Y||z9.has(J))return J}for(let W of Z){if(Y){let q=jX[W];if(q!=null)return q}let G=BX[W];if(G!=null){if(Y||z9.has(G))return G}}return"default"}function FX(X){return X.spriteSheet!=null||X.remap!=null||X.byFileName!=null||X.byFileExtension!=null||X.byFileNameContains!=null}function G6(X){if(X==null)return{set:"complete",colored:!0};if(typeof X==="string")return{set:X,colored:!0};return{...X,set:X.set??(FX(X)?"none":"complete"),colored:X.colored??!0}}var $7={compact:{itemHeight:24,factor:0.8},default:{itemHeight:30,factor:1},relaxed:{itemHeight:36,factor:1.2}};function O9(X,Q){if(typeof X==="number")return{itemHeight:Q??$7.default.itemHeight,factor:X};let Z=$7[X??"default"];return{itemHeight:Q??Z.itemHeight,factor:Z.factor}}var U7=$7.default.itemHeight,B9=10,z7=420;var r7=`@layer base, theme, unsafe;

@layer base {
  :host {
    /*
      CSS variables use a fallback stack to ensure user and theme colors slot
      in with ease. User colors take precedence over theme colors, which take
      precedence over defaults.

      Fallback order:

      1. --trees-*-override (explicit)
      2. --trees-theme-* (e.g. Shiki/VS Code tokens)
      3. defaults

      Theme variable names mirror Shiki/VS Code theme file JSON tokens.

      // Available CSS Color Overrides
      --trees-fg-override
      --trees-fg-muted-override
      --trees-bg-override
      --trees-bg-muted-override
      --trees-accent-override
      --trees-border-color-override

      --trees-focus-ring-color-override
      --trees-focus-ring-width-override
      --trees-focus-ring-offset-override

      --trees-search-fg-override
      --trees-search-font-weight-override
      --trees-search-bg-override

      --trees-selected-fg-override
      --trees-selected-bg-override
      --trees-selected-focused-border-color-override

      // Git Status Color Overrides
      --trees-status-added-override
      --trees-status-ignored-override
      --trees-status-modified-override
      --trees-status-renamed-override
      --trees-status-untracked-override
      --trees-status-deleted-override
      --trees-git-added-color-override
      --trees-git-ignored-color-override
      --trees-git-modified-color-override
      --trees-git-renamed-color-override
      --trees-git-untracked-color-override
      --trees-git-deleted-color-override

      // Built-in File Icon Color Overrides
      --trees-file-icon-color
      --trees-file-icon-color-astro
      --trees-file-icon-color-babel
      --trees-file-icon-color-bash
      --trees-file-icon-color-biome
      --trees-file-icon-color-bootstrap
      --trees-file-icon-color-browserslist
      --trees-file-icon-color-bun
      --trees-file-icon-color-claude
      --trees-file-icon-color-css
      --trees-file-icon-color-database
      --trees-file-icon-color-default
      --trees-file-icon-color-docker
      --trees-file-icon-color-eslint
      --trees-file-icon-color-git
      --trees-file-icon-color-go
      --trees-file-icon-color-graphql
      --trees-file-icon-color-html
      --trees-file-icon-color-image
      --trees-file-icon-color-javascript
      --trees-file-icon-color-json
      --trees-file-icon-color-markdown
      --trees-file-icon-color-mcp
      --trees-file-icon-color-npm
      --trees-file-icon-color-oxc
      --trees-file-icon-color-postcss
      --trees-file-icon-color-prettier
      --trees-file-icon-color-python
      --trees-file-icon-color-react
      --trees-file-icon-color-ruby
      --trees-file-icon-color-rust
      --trees-file-icon-color-sass
      --trees-file-icon-color-svg
      --trees-file-icon-color-svelte
      --trees-file-icon-color-svgo
      --trees-file-icon-color-swift
      --trees-file-icon-color-table
      --trees-file-icon-color-text
      --trees-file-icon-color-tailwind
      --trees-file-icon-color-terraform
      --trees-file-icon-color-typescript
      --trees-file-icon-color-vite
      --trees-file-icon-color-vscode
      --trees-file-icon-color-vue
      --trees-file-icon-color-wasm
      --trees-file-icon-color-webpack
      --trees-file-icon-color-yml
      --trees-file-icon-color-zig
      --trees-file-icon-color-zip

      // Density
      //
      // A unitless scale factor for padding, gaps, and indentation. Usually
      // set via \`density\` on useFileTree. Individual overrides take precedence.
      //
      //   Compact: 0.8
      //   Default: 1
      //   Relaxed: 1.2
      //
      --trees-density-override

      // Available CSS Layout Overrides
      --trees-gap-override
      --trees-border-radius-override
      --trees-font-family-override
      --trees-font-size-override
      --trees-font-weight-regular-override
      --trees-font-weight-semibold-override
      --trees-level-gap-override
      --trees-item-padding-x-override
      --trees-item-margin-x-override
      --trees-item-row-gap-override
      --trees-icon-width-override
      --trees-icon-nudge-override
      --trees-scrollbar-gutter-override
      --trees-padding-inline-override
    */

    --trees-accent: var(--trees-accent-override, #009fff);
    --trees-fg: var(
      --trees-fg-override,
      var(--trees-theme-sidebar-fg, light-dark(#6c6c71, #adadb1))
    );
    --trees-fg-muted: var(
      --trees-fg-muted-override,
      var(--trees-theme-sidebar-header-fg, light-dark(#84848a, #84848a))
    );
    --trees-bg: var(
      --trees-bg-override,
      var(--trees-theme-sidebar-bg, light-dark(#f8f8f8, #141415))
    );
    /* var(--trees-theme-list-hover-bg, light-dark(#dfebff59, #19283c59)) */
    --trees-bg-muted: var(
      --trees-bg-muted-override,
      var(
        --trees-theme-list-hover-bg,
        light-dark(
          color-mix(
            in lab,
            var(--trees-accent) var(--trees-bg-alpha-light, 8%),
            var(--trees-bg)
          ),
          color-mix(
            in lab,
            var(--trees-accent) var(--trees-bg-alpha-dark, 10%),
            var(--trees-bg)
          )
        )
      )
    );
    --trees-input-bg: var(
      --trees-input-bg-override,
      light-dark(#f8f8f8, #070707)
    );

    --trees-added-light: #16a994;
    --trees-added-dark: #00cab1;
    --trees-ignored-light: #adadb1;
    --trees-ignored-dark: #4a4a4e;
    --trees-modified-light: #1ca1c7;
    --trees-modified-dark: #08c0ef;
    --trees-renamed-light: #d5a910;
    --trees-renamed-dark: #ffd452;
    --trees-untracked-light: #16a994;
    --trees-untracked-dark: #00cab1;
    --trees-deleted-light: #ff2e3f;
    --trees-deleted-dark: #ff6762;

    --trees-border-color: var(
      --trees-border-color-override,
      var(--trees-theme-sidebar-border, light-dark(#eeeeef, #070707))
    );
    --trees-indent-guide-bg: var(
      --trees-indent-guide-bg-override,
      color-mix(in lab, var(--trees-fg-muted) 25%, transparent)
    );
    --trees-density: var(--trees-density-override, 1);
    --trees-border-radius: var(
      --trees-border-radius-override,
      calc(6px * var(--trees-density))
    );

    --trees-font-family: var(--trees-font-family-override, system-ui);
    --trees-font-size: var(--trees-font-size-override, 13px);
    --trees-font-weight-regular: var(--trees-font-weight-regular-override, 400);
    --trees-font-weight-semibold: var(
      --trees-font-weight-semibold-override,
      600
    );

    --trees-focus-ring-color: var(
      --trees-focus-ring-color-override,
      var(--trees-theme-focus-ring, var(--trees-accent))
    );
    --trees-focus-ring-width: var(--trees-focus-ring-width-override, 1px);
    --trees-focus-ring-offset: var(--trees-focus-ring-offset-override, -1px);

    --trees-search-fg: var(
      --trees-search-fg-override,
      var(--trees-theme-input-fg, var(--trees-fg))
    );
    --trees-search-font-weight: var(--trees-search-font-weight-override, 600);
    --trees-search-bg: var(
      --trees-search-bg-override,
      var(--trees-theme-input-bg, var(--trees-input-bg))
    );

    --trees-scrollbar-thumb: var(
      --trees-scrollbar-thumb-override,
      var(
        --trees-theme-scrollbar-thumb,
        color-mix(in lab, var(--trees-fg) 25%, var(--trees-bg))
      )
    );

    --trees-selected-fg: var(
      --trees-selected-fg-override,
      var(--trees-theme-list-active-selection-fg, var(--trees-fg))
    );
    --trees-selected-bg: var(
      --trees-selected-bg-override,
      var(
        --trees-theme-list-active-selection-bg,
        light-dark(
          color-mix(in lab, var(--trees-accent) 12%, var(--trees-bg)),
          color-mix(in lab, var(--trees-accent) 15%, var(--trees-bg))
        )
      )
    );
    --trees-selected-focused-border-color: var(
      --trees-selected-focused-border-color-override,
      var(--trees-theme-focus-ring, var(--trees-accent))
    );

    /* Git status (e.g. from Shiki theme gitDecoration.*) */
    --trees-status-added: var(
      --trees-status-added-override,
      var(
        --trees-theme-git-added-fg,
        light-dark(var(--trees-added-light), var(--trees-added-dark))
      )
    );
    --trees-status-ignored: var(
      --trees-status-ignored-override,
      var(
        --trees-theme-git-ignored-fg,
        light-dark(var(--trees-ignored-light), var(--trees-ignored-dark))
      )
    );
    --trees-status-modified: var(
      --trees-status-modified-override,
      var(
        --trees-theme-git-modified-fg,
        light-dark(var(--trees-modified-light), var(--trees-modified-dark))
      )
    );
    --trees-status-renamed: var(
      --trees-status-renamed-override,
      var(
        --trees-theme-git-renamed-fg,
        light-dark(var(--trees-renamed-light), var(--trees-renamed-dark))
      )
    );
    --trees-status-untracked: var(
      --trees-status-untracked-override,
      var(
        --trees-theme-git-untracked-fg,
        light-dark(var(--trees-untracked-light), var(--trees-untracked-dark))
      )
    );
    --trees-status-deleted: var(
      --trees-status-deleted-override,
      var(
        --trees-theme-git-deleted-fg,
        light-dark(var(--trees-deleted-light), var(--trees-deleted-dark))
      )
    );
    --trees-git-modified-color: var(
      --trees-git-modified-color-override,
      var(--trees-status-modified)
    );
    --trees-git-added-color: var(
      --trees-git-added-color-override,
      var(--trees-status-added)
    );
    --trees-git-ignored-color: var(
      --trees-git-ignored-color-override,
      var(--trees-status-ignored)
    );
    --trees-git-deleted-color: var(
      --trees-git-deleted-color-override,
      var(--trees-status-deleted)
    );
    --trees-git-renamed-color: var(
      --trees-git-renamed-color-override,
      var(--trees-status-renamed)
    );
    --trees-git-untracked-color: var(
      --trees-git-untracked-color-override,
      var(--trees-status-untracked)
    );

    --trees-icon-gray: light-dark(#84848a, #adadb1);
    --trees-icon-red: light-dark(#d52c36, #ff6762);
    --trees-icon-vermilion: light-dark(#ff8c5b, #d5512f);
    --trees-icon-orange: light-dark(#d47628, #ffa359);
    --trees-icon-yellow: light-dark(#d5a910, #ffd452);
    --trees-icon-green: light-dark(#199f43, #5ecc71);
    --trees-icon-teal: light-dark(#17a5af, #64d1db);
    --trees-icon-cyan: light-dark(#1ca1c7, #68cdf2);
    --trees-icon-blue: light-dark(#1a85d4, #69b1ff);
    --trees-icon-indigo: light-dark(#693acf, #9d6afb);
    --trees-icon-purple: light-dark(#a631be, #d568ea);
    --trees-icon-pink: light-dark(#d32a61, #ff678d);
    --trees-icon-mauve: light-dark(#594c5b, #79697b);

    --trees-file-icon-color-default: var(
      --trees-file-icon-color,
      var(--trees-icon-gray)
    );
    --trees-file-icon-color-astro: var(
      --trees-file-icon-color,
      var(--trees-icon-purple)
    );
    --trees-file-icon-color-babel: var(
      --trees-file-icon-color,
      var(--trees-icon-yellow)
    );
    --trees-file-icon-color-bash: var(
      --trees-file-icon-color,
      var(--trees-icon-green)
    );
    --trees-file-icon-color-biome: var(
      --trees-file-icon-color,
      var(--trees-icon-blue)
    );
    --trees-file-icon-color-bootstrap: var(
      --trees-file-icon-color,
      var(--trees-icon-indigo)
    );
    --trees-file-icon-color-browserslist: var(
      --trees-file-icon-color,
      var(--trees-icon-yellow)
    );
    --trees-file-icon-color-bun: var(
      --trees-file-icon-color,
      var(--trees-icon-mauve)
    );
    --trees-file-icon-color-claude: var(
      --trees-file-icon-color,
      var(--trees-icon-orange)
    );
    --trees-file-icon-color-css: var(
      --trees-file-icon-color,
      var(--trees-icon-indigo)
    );
    --trees-file-icon-color-database: var(
      --trees-file-icon-color,
      var(--trees-icon-purple)
    );
    --trees-file-icon-color-docker: var(
      --trees-file-icon-color,
      var(--trees-icon-blue)
    );
    --trees-file-icon-color-eslint: var(
      --trees-file-icon-color,
      var(--trees-icon-indigo)
    );
    --trees-file-icon-color-git: var(
      --trees-file-icon-vermilion,
      var(--trees-icon-vermilion)
    );
    --trees-file-icon-color-go: var(
      --trees-file-icon-color,
      var(--trees-icon-cyan)
    );
    --trees-file-icon-color-graphql: var(
      --trees-file-icon-color,
      var(--trees-icon-pink)
    );
    --trees-file-icon-color-html: var(
      --trees-file-icon-color,
      var(--trees-icon-orange)
    );
    --trees-file-icon-color-image: var(
      --trees-file-icon-color,
      var(--trees-icon-pink)
    );
    --trees-file-icon-color-javascript: var(
      --trees-file-icon-color,
      var(--trees-icon-yellow)
    );
    --trees-file-icon-color-json: var(
      --trees-file-icon-color,
      var(--trees-icon-orange)
    );
    --trees-file-icon-color-markdown: var(
      --trees-file-icon-color,
      var(--trees-icon-green)
    );
    --trees-file-icon-color-mcp: var(
      --trees-file-icon-color,
      var(--trees-icon-teal)
    );
    --trees-file-icon-color-npm: var(
      --trees-file-icon-color,
      var(--trees-icon-red)
    );
    --trees-file-icon-color-oxc: var(
      --trees-file-icon-cyan,
      var(--trees-icon-cyan)
    );
    --trees-file-icon-color-postcss: var(
      --trees-file-icon-color,
      var(--trees-icon-red)
    );
    --trees-file-icon-color-prettier: var(
      --trees-file-icon-color,
      var(--trees-icon-teal)
    );
    --trees-file-icon-color-python: var(
      --trees-file-icon-color,
      var(--trees-icon-blue)
    );
    --trees-file-icon-color-react: var(
      --trees-file-icon-color,
      var(--trees-icon-cyan)
    );
    --trees-file-icon-color-ruby: var(
      --trees-file-icon-color,
      var(--trees-icon-red)
    );
    --trees-file-icon-color-rust: var(
      --trees-file-icon-color,
      var(--trees-icon-orange)
    );
    --trees-file-icon-color-sass: var(
      --trees-file-icon-color,
      var(--trees-icon-pink)
    );
    --trees-file-icon-color-svg: var(
      --trees-file-icon-color,
      var(--trees-icon-orange)
    );
    --trees-file-icon-color-svelte: var(
      --trees-file-icon-color,
      var(--trees-icon-red)
    );
    --trees-file-icon-color-svgo: var(
      --trees-file-icon-color,
      var(--trees-icon-green)
    );
    --trees-file-icon-color-swift: var(
      --trees-file-icon-color,
      var(--trees-icon-orange)
    );
    --trees-file-icon-color-table: var(
      --trees-file-icon-color,
      var(--trees-icon-teal)
    );
    --trees-file-icon-color-text: var(
      --trees-file-icon-color,
      var(--trees-icon-gray)
    );
    --trees-file-icon-color-tailwind: var(
      --trees-file-icon-color,
      var(--trees-icon-cyan)
    );
    --trees-file-icon-color-terraform: var(
      --trees-file-icon-color,
      var(--trees-icon-indigo)
    );
    --trees-file-icon-color-typescript: var(
      --trees-file-icon-color,
      var(--trees-icon-blue)
    );
    --trees-file-icon-color-vite: var(
      --trees-file-icon-color,
      var(--trees-icon-purple)
    );
    --trees-file-icon-color-vscode: var(
      --trees-file-icon-color,
      var(--trees-icon-blue)
    );
    --trees-file-icon-color-vue: var(
      --trees-file-icon-color,
      var(--trees-icon-green)
    );
    --trees-file-icon-color-wasm: var(
      --trees-file-icon-color,
      var(--trees-icon-indigo)
    );
    --trees-file-icon-color-webpack: var(
      --trees-file-icon-color,
      var(--trees-icon-blue)
    );
    --trees-file-icon-color-yml: var(
      --trees-file-icon-color,
      var(--trees-icon-red)
    );
    --trees-file-icon-color-zig: var(
      --trees-file-icon-color,
      var(--trees-icon-orange)
    );
    --trees-file-icon-color-zip: var(
      --trees-file-icon-color,
      var(--trees-icon-orange)
    );

    --trees-level-gap: var(
      --trees-level-gap-override,
      calc(8px * var(--trees-density))
    );
    --trees-item-padding-x: var(
      --trees-item-padding-x-override,
      calc(8px * var(--trees-density))
    );
    --trees-item-margin-x: var(
      --trees-item-margin-x-override,
      calc(2px * var(--trees-density))
    );
    --trees-item-row-gap: var(
      --trees-item-row-gap-override,
      calc(6px * var(--trees-density))
    );
    --trees-icon-width: var(--trees-icon-width-override, 16px);
    --trees-icon-nudge: var(
      --trees-icon-nudge-override,
      calc(1px * var(--trees-density))
    );
    --trees-row-height: var(--trees-item-height, 30px);
    --trees-git-lane-width: var(--trees-git-lane-width-override, 12px);
    --trees-action-lane-width: var(
      --trees-action-lane-width-override,
      calc(var(--trees-icon-width) + 2px)
    );
    /* Keep the floating trigger aligned with the row's action lane. Going in
       from the root's right edge: the scroll container reserves
       \`--trees-padding-inline\` of effective inset on each side (its asymmetric
       padding formula cancels the scrollbar gutter on the right), the row
       sits inside that inset, and its trailing \`--trees-item-padding-x\` is the
       action lane itself. The trigger's own focus-ring margin then trims one
       pixel back so the button's visible right edge lines up with the lane. */
    --trees-context-menu-trigger-inline-offset: calc(
      var(--trees-padding-inline) + var(--trees-item-padding-x) -
        var(--trees-focus-ring-width)
    );

    --trees-scrollbar-gutter: var(--trees-scrollbar-gutter-override, 6px);
    --trees-padding-inline: var(--trees-padding-inline-override, 16px);

    color-scheme: light dark;
    display: flex;
    flex-direction: column;
    font-size: var(--trees-font-size);
    color: var(--trees-fg);
    background-color: var(--trees-bg);
    --truncate-marker-background-color: var(--trees-bg);
    --truncate-marker-background-overlay-color: transparent;
    font-family: var(--trees-font-family);
    font-weight: var(--trees-font-weight-regular);
  }

  :host([data-file-tree-virtualized='true']) {
    height: 100%;
    overflow: hidden;
  }

  [data-file-tree-virtualized-wrapper='true'] {
    height: 100%;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  [data-file-tree-virtualized-root='true'] {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  [data-file-tree-virtualized-scroll='true'],
  [data-file-tree-scrollbar-measure='true'] {
    overflow-y: auto;
    scrollbar-gutter: stable;

    &::-webkit-scrollbar {
      width: var(--trees-scrollbar-gutter);
      height: var(--trees-scrollbar-gutter);
    }

    &::-webkit-scrollbar-track {
      background: transparent;
    }

    &::-webkit-scrollbar-thumb {
      background-color: var(--trees-scrollbar-thumb);
      border: 1px solid transparent;
      background-clip: content-box;
      border-radius: calc(var(--trees-scrollbar-gutter) / 2);
    }

    &::-webkit-scrollbar-corner {
      background-color: transparent;
    }
  }

  /* These are styles for a temporarily generated element to measure the size
   * of the scrollbar.  It's intended to be somewhat similar in scrollbar style
   * scope to the scrollable tree so \`--trees-scrollbar-gutter-measured\` is an
   * accurate reflection of the size the scrollbar gutter takes up. */
  [data-file-tree-scrollbar-measure='true'] {
    position: absolute;
    top: 0;
    left: 0;
    visibility: hidden;
    pointer-events: none;
    width: 100px;
    height: 100px;
  }

  @supports (-moz-appearance: none) {
    [data-file-tree-virtualized-scroll='true'],
    [data-file-tree-scrollbar-measure='true'] {
      scrollbar-width: thin;
      scrollbar-color: var(--trees-scrollbar-thumb) transparent;
    }
  }

  [data-file-tree-virtualized-scroll='true'] {
    position: relative;
    overflow-y: auto;
    flex: 1 1 0;
    min-height: 0;
    padding-inline: max(
        calc(var(--trees-padding-inline) - var(--trees-item-margin-x)),
        0px
      )
      /* NOTE(amadeus): We can assume that all Webkit based browser gutters
       * will align to the value of '--trees-scrollbar-gutter', however if not, then
       * \`--trees-scrollbar-gutter-measured\` should correct it. Mostly we are
       * hoping to avoid SSR alignment jumps if possible. In non-SSR'd environments
       * \`--trees-scrollbar-gutter-measured\` should always be immediately available.
       */
      max(
        calc(
          var(--trees-padding-inline) - var(--trees-item-margin-x) -
            var(
              --trees-scrollbar-gutter-measured,
              var(--trees-scrollbar-gutter)
            )
        ),
        0px
      );
  }

  @supports (-moz-appearance: none) {
    [data-file-tree-virtualized-scroll='true'] {
      padding-inline: max(
          calc(var(--trees-padding-inline) - var(--trees-item-margin-x)),
          0px
        )
        /* NOTE(amadeus): However on Firefox it can vary a little bit, but most
         * likely the majority of cases will default to a 0px width scrollbar lets
         * inherit that first to avoid SSR jumps. In non-SSR'd environments
         * \`--trees-scrollbar-gutter-measured\` should always be immediately available.
         */
        max(
          calc(
            var(--trees-padding-inline) - var(--trees-item-margin-x) -
              var(--trees-scrollbar-gutter-measured, 0px)
          ),
          0px
        );
    }
  }

  [data-file-tree-sticky-overlay='true'] {
    position: sticky;
    top: 0;
    height: 0;
    z-index: 4;
    overflow: visible;
    pointer-events: none;
  }

  /* The overlay DOM is kept populated even at scrollTop=0 so the browser has
   * the rendered rows on hand the moment scrolling begins — otherwise the
   * compositor paints a scrolled frame before React can mount the overlay,
   * and the topmost sticky folder jumps up by a couple of pixels before it
   * "snaps" into its pinned position. We hide it via CSS whenever the scroll
   * is at the top and no scroll is in progress, so the preview doesn't leak
   * through at rest. \`data-overlay-reveal\` is stamped on the root only when
   * the user initiates a scroll while already at the top — exactly the case
   * where we need the pre-mounted overlay to be visible through the first
   * compositor frame. It is deliberately distinct from the general
   * \`data-is-scrolling\` flag so a scroll that ends at the top (e.g. ArrowUp
   * navigation) re-hides the overlay the instant the scroll lands, rather
   * than waiting for the hover-suppression timer to elapse. */
  [data-file-tree-virtualized-root='true'][data-scroll-at-top='true']:not(
      [data-overlay-reveal]
    )
    [data-file-tree-sticky-overlay='true'] {
    visibility: hidden;
  }

  [data-file-tree-sticky-overlay-content='true'] {
    background-color: var(--trees-bg);
    position: relative;
    pointer-events: none;
  }

  [data-file-tree-virtualized-list='true'] {
    background-color: var(--trees-bg);
    position: relative;
    min-height: 100%;
    width: 100%;
    overflow-anchor: none;

    &[data-is-scrolling] {
      pointer-events: none;
    }
  }

  [data-file-tree-virtualized-sticky-offset='true'] {
    contain: layout size;
  }

  [data-file-tree-virtualized-sticky='true'] {
    position: sticky;
    top: 0;
    width: 100%;
    display: flex;
    flex-direction: column;
    isolation: isolate;
    /* Promote to its own compositor layer so text inside the window is
     * rasterized once and GPU-translated during scroll. Without this, the
     * browser re-paints the window (and its text) at every scroll frame,
     * which produces visible 1px shake / character tearing. */
    will-change: transform;
  }

  [data-file-tree-search-container] {
    display: flex;
    padding: 0;
    padding-inline: var(--trees-padding-inline);
    margin-bottom: var(--trees-item-row-gap);
  }

  [data-file-tree-search-input] {
    --trees-focus-ring-width: 2px;
    font-family: var(--trees-font-family);
    font-size: var(--trees-font-size);
    flex: 1;
    height: var(--trees-row-height);
    /* 1px breathing room so the focus-visible outline isn't clipped when the
     * input sits flush against the top of the scroll container. */
    margin-block: 1px;
    padding-inline: var(--trees-item-padding-x);
    line-height: var(--trees-row-height);
    color: var(--trees-search-fg);
    background-color: var(--trees-search-bg);
    border: 1px solid var(--trees-border-color);
    border-radius: var(--trees-border-radius);
    outline: none;

    &::placeholder {
      color: color-mix(
        in lab,
        var(--trees-search-fg) 65%,
        var(--trees-search-bg)
      );
    }

    &:focus-visible,
    &[data-file-tree-search-input-fake-focus='true'] {
      outline: var(--trees-focus-ring-width) solid var(--trees-focus-ring-color);
      outline-offset: var(--trees-focus-ring-offset);
    }
  }

  /* The wrapper for the tree items */
  [role='tree'] {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: var(--trees-gap-override, 0);
  }

  /* LIST ITEM */
  [data-type='item'] {
    color: inherit;
    font-family: var(--trees-font-family);
    font-size: var(--trees-font-size);
    text-align: start;
    outline: none;
    background-color: var(--trees-bg);
    border: none;
    position: relative;

    padding: 0 var(--trees-item-padding-x);
    margin: 0 var(--trees-item-margin-x);
    cursor: pointer;
    -webkit-user-select: none;
            user-select: none;
    -webkit-touch-callout: none;
    touch-action: manipulation;
    display: flex;
    flex: 0 0 var(--trees-row-height);
    align-items: center;
    height: var(--trees-row-height);
    line-height: var(--trees-row-height);
    gap: var(--trees-item-row-gap);
    border-radius: var(--trees-border-radius);
    /* Row states may be translucent, so markers paint the tree background first
     * and then the state color on top to avoid compositing the same alpha twice. */
    --truncate-marker-background-color: var(--trees-bg);
    --truncate-marker-background-overlay-color: transparent;
    --truncate-marker-block-inset: 0px;

    &:hover,
    &[data-item-context-hover='true'] {
      background-color: var(--trees-bg-muted);
      --truncate-marker-background-overlay-color: var(--trees-bg-muted);
    }

    &[data-item-focused='true'],
    &:focus-visible {
      z-index: 2;

      /* Flattened segment markers sit high enough to cover the row outline unless
       * their painted background is inset by the focus ring width. */
      [data-item-flattened-subitems] {
        --truncate-marker-block-inset: var(--trees-focus-ring-width);
      }

      &::before {
        position: absolute;
        inset: 0;
        content: '';
        display: block;
        border-radius: var(--trees-border-radius);
        outline: var(--trees-focus-ring-width) solid
          var(--trees-focus-ring-color);
        outline-offset: var(--trees-focus-ring-offset);
        pointer-events: none;
      }

      &[data-item-selected='true']::before {
        outline-color: var(--trees-selected-focused-border-color);
      }
    }

    &[data-item-selected='true'] {
      color: var(--trees-selected-fg);
      background-color: var(--trees-selected-bg);
      --truncate-marker-background-overlay-color: var(--trees-selected-bg);
      z-index: 3;

      [data-item-section='icon'] {
        color: var(--trees-selected-fg);
      }
    }

    &[data-item-search-match='true'] {
      font-weight: var(--trees-search-font-weight);
    }
  }

  [data-type='item'][data-file-tree-sticky-row='true'] {
    pointer-events: auto;
  }

  /* Sticky rows opt back into pointer events because the overlay wrapper is
   * inert. During scroll, put them back under the same hover suppression as
   * the virtualized list so translucent hover states and menu triggers do not
   * paint over rows moving beneath the sticky stack. */
  [data-file-tree-virtualized-root='true'][data-is-scrolling]
    [data-type='item'][data-file-tree-sticky-row='true'] {
    pointer-events: none;
  }

  [data-file-tree-virtualized-root='true'][data-is-scrolling]
    [data-type='item'][data-file-tree-sticky-row='true']:hover:not(
      [data-item-selected='true']
    ),
  [data-file-tree-virtualized-root='true'][data-is-scrolling]
    [data-type='item'][data-file-tree-sticky-row='true'][data-item-context-hover='true']:not(
      [data-item-selected='true']
    ) {
    background-color: var(--trees-bg);
    --truncate-marker-background-overlay-color: transparent;
  }

  [data-item-selected='true']:has(+ [data-item-selected='true']) {
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }

  [data-item-selected='true'] + [data-item-selected='true'] {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }

  /* Flattened Directory Parts */
  [data-item-flattened-subitems] {
    display: inline-flex;
    align-items: center;
    gap: 2px;
  }
  [data-item-flattened-subitem]:hover,
  [data-item-flattened-subitem-drag-target='true'] {
    text-decoration: underline;
  }

  /* Icon for each item */
  [data-item-section='icon'] {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--trees-fg-muted);
    fill: currentColor;
    width: var(--trees-icon-width);
  }

  :where([data-item-section='icon'] > [data-icon-token]) {
    color: var(--trees-fg-muted);
  }

  [data-file-tree-colored-icons='true'] {
    [data-icon-token='astro'] {
      color: var(--trees-file-icon-color-astro);
    }
    [data-icon-token='babel'] {
      color: var(--trees-file-icon-color-babel);
    }
    [data-icon-token='bash'] {
      color: var(--trees-file-icon-color-bash);
    }
    [data-icon-token='biome'] {
      color: var(--trees-file-icon-color-biome);
    }
    [data-icon-token='bootstrap'] {
      color: var(--trees-file-icon-color-bootstrap);
    }
    [data-icon-token='browserslist'] {
      color: var(--trees-file-icon-color-browserslist);
    }
    [data-icon-token='bun'] {
      color: var(--trees-file-icon-color-bun);
    }
    [data-icon-token='claude'] {
      color: var(--trees-file-icon-color-claude);
    }
    [data-icon-token='css'] {
      color: var(--trees-file-icon-color-css);
    }
    [data-icon-token='database'] {
      color: var(--trees-file-icon-color-database);
    }
    [data-icon-token='default'] {
      color: var(--trees-file-icon-color-default);
    }
    [data-icon-token='docker'] {
      color: var(--trees-file-icon-color-docker);
    }
    [data-icon-token='eslint'] {
      color: var(--trees-file-icon-color-eslint);
    }
    [data-icon-token='git'] {
      color: var(--trees-file-icon-color-git);
    }
    [data-icon-token='go'] {
      color: var(--trees-file-icon-color-go);
    }
    [data-icon-token='graphql'] {
      color: var(--trees-file-icon-color-graphql);
    }
    [data-icon-token='html'] {
      color: var(--trees-file-icon-color-html);
    }
    [data-icon-token='image'] {
      color: var(--trees-file-icon-color-image);
    }
    [data-icon-token='javascript'] {
      color: var(--trees-file-icon-color-javascript);
    }
    [data-icon-token='json'] {
      color: var(--trees-file-icon-color-json);
    }
    [data-icon-token='markdown'] {
      color: var(--trees-file-icon-color-markdown);
    }
    [data-icon-token='mcp'] {
      color: var(--trees-file-icon-color-mcp);
    }
    [data-icon-token='npm'] {
      color: var(--trees-file-icon-color-npm);
    }
    [data-icon-token='oxc'] {
      color: var(--trees-file-icon-color-oxc);
    }
    [data-icon-token='postcss'] {
      color: var(--trees-file-icon-color-postcss);
    }
    [data-icon-token='prettier'] {
      color: var(--trees-file-icon-color-prettier);
    }
    [data-icon-token='python'] {
      color: var(--trees-file-icon-color-python);
    }
    [data-icon-token='react'] {
      color: var(--trees-file-icon-color-react);
    }
    [data-icon-token='ruby'] {
      color: var(--trees-file-icon-color-ruby);
    }
    [data-icon-token='rust'] {
      color: var(--trees-file-icon-color-rust);
    }
    [data-icon-token='sass'] {
      color: var(--trees-file-icon-color-sass);
    }
    [data-icon-token='svg'] {
      color: var(--trees-file-icon-color-svg);
    }
    [data-icon-token='svelte'] {
      color: var(--trees-file-icon-color-svelte);
    }
    [data-icon-token='svgo'] {
      color: var(--trees-file-icon-color-svgo);
    }
    [data-icon-token='swift'] {
      color: var(--trees-file-icon-color-swift);
    }
    [data-icon-token='table'] {
      color: var(--trees-file-icon-color-table);
    }
    [data-icon-token='text'] {
      color: var(--trees-file-icon-color-text);
    }
    [data-icon-token='tailwind'] {
      color: var(--trees-file-icon-color-tailwind);
    }
    [data-icon-token='terraform'] {
      color: var(--trees-file-icon-color-terraform);
    }
    [data-icon-token='typescript'] {
      color: var(--trees-file-icon-color-typescript);
    }
    [data-icon-token='vite'] {
      color: var(--trees-file-icon-color-vite);
    }
    [data-icon-token='vscode'] {
      color: var(--trees-file-icon-color-vscode);
    }
    [data-icon-token='vue'] {
      color: var(--trees-file-icon-color-vue);
    }
    [data-icon-token='wasm'] {
      color: var(--trees-file-icon-color-wasm);
    }
    [data-icon-token='webpack'] {
      color: var(--trees-file-icon-color-webpack);
    }
    [data-icon-token='yml'] {
      color: var(--trees-file-icon-color-yml);
    }
    [data-icon-token='zig'] {
      color: var(--trees-file-icon-color-zig);
    }
    [data-icon-token='zip'] {
      color: var(--trees-file-icon-color-zip);
    }
  }

  /* Chevron rotation and visual alignment */
  /* Chevron pointing down */
  [data-icon-name='file-tree-icon-chevron'] {
    &[data-align-capitals='false'] {
      transform: translate(0, var(--trees-icon-nudge));
    }
    &[data-align-capitals='true'] {
      transform: translate(0, 0);
    }
  }

  [data-item-section='content'] {
    flex: 0 1 auto;
    text-align: start;
    min-width: 0;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    /* Breaks middle truncate component to also set this */
    /* white-space: nowrap; */
  }

  [data-item-section='decoration'] {
    flex: 1 1 0;
    min-width: 0;
    display: flex;
    justify-content: flex-end;
    text-align: end;
    overflow: hidden;
    color: var(--trees-fg-muted);
  }

  [data-item-section='decoration'] > span {
    min-width: 0;
    max-width: 100%;
    display: inline-flex;
    align-items: center;
    justify-content: flex-end;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  [data-item-section='git'],
  [data-item-section='action'] {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  [data-item-section='git'] {
    width: var(--trees-git-lane-width);
  }

  [data-item-section='action'] {
    width: var(--trees-action-lane-width);
    color: var(--trees-fg-muted);
    fill: currentColor;
    pointer-events: none;
  }

  [data-item-section='git'] > span,
  [data-item-section='action'] > span {
    width: 100%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  [data-item-action-affordance='decorative'] {
    opacity: 0.85;
  }

  [data-item-rename-input] {
    appearance: none;
    width: 100%;
    min-width: 0;
    height: calc(var(--trees-row-height) - 4px);
    font-family: inherit;
    font-size: inherit;
    /* line-height: calc(var(--trees-row-height) - 8px); */
    color: inherit;
    background-color: transparent;
    border: 0;
    padding-inline: 6px;
    outline: none;
    box-sizing: border-box;
  }

  [data-item-section='content']:has([data-item-rename-input])
    ~ [data-item-section='action'],
  [data-item-section='content']:has([data-item-rename-input])
    ~ [data-item-section='decoration'] {
    display: none;
  }

  /* Chevron pointing right */
  [aria-expanded='false'][data-item-type='folder']
    > [data-item-section='icon']
    > [data-icon-name='file-tree-icon-chevron'] {
    &[data-align-capitals='true'] {
      transform: rotate(-90deg)
        translate(
          calc(var(--trees-icon-nudge) / 2),
          calc(var(--trees-icon-nudge) / 2)
        );
    }
    &[data-align-capitals='false'] {
      transform: rotate(-90deg)
        translate(
          calc(var(--trees-icon-nudge) / 2 * -1),
          calc(var(--trees-icon-nudge) / 2)
        );
    }
  }

  /* LIST IDENTATION */
  /* Spacing container */
  [data-item-section='spacing'] {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    height: var(--trees-row-height);
    padding-left: calc(calc(var(--trees-icon-width) / 2) - 0.5px);

    &:empty {
      padding-left: 0;
    }
  }

  /* Spacing per level */
  [data-item-section='spacing-item'] {
    transform: translateX(-0.25px);
    display: inline-block;
    border-left: 1px solid var(--trees-indent-guide-bg);
    height: 100%;
    margin-right: calc(var(--trees-level-gap) - 1px);
    opacity: 0;
    transition: opacity 150ms ease;

    & + & {
      margin-left: calc(
        var(--trees-item-row-gap) + calc(var(--trees-icon-width) / 2) - 0.5px
      );
    }
  }

  :host(:hover) [data-item-section='spacing-item'] {
    opacity: 0.75;
  }

  /* Git status indicator */

  /* This is a folder that contains a git change */
  [data-item-contains-git-change='true'] > [data-item-section='git'] {
    color: var(--trees-git-modified-color);
    opacity: 0.5;
    fill: currentColor;
  }

  /* These are files that have a git change */
  [data-item-git-status] {
    &
      > :where([data-item-section='icon'])
      > :where(:not([data-icon-name='file-tree-icon-chevron'])) {
      color: var(--trees-item-git-status-color);
    }
    & > [data-item-section='content'] {
      color: var(--trees-item-git-status-color);
    }
    & > [data-item-section='git'] {
      color: var(--trees-item-git-status-color);
      font-weight: var(--trees-font-weight-semibold);
    }
  }

  [data-item-git-status='added'] {
    --trees-item-git-status-color: var(--trees-git-added-color);
  }

  [data-item-git-status='deleted'] {
    --trees-item-git-status-color: var(--trees-git-deleted-color);
  }

  [data-item-git-status='ignored'] {
    --trees-item-git-status-color: var(--trees-git-ignored-color);

    & > [data-item-section='icon'] {
      opacity: 0.5;
    }
  }

  [data-item-section='git'] [data-icon-name='file-tree-icon-dot'] {
    /* this is a nudge to align the dot with the likely lowercase text. it's slightly
    generalizable, but other fonts are gonna need other nudges i assume */
    transform: translateY(calc(0.65ex - 50%));
  }

  [data-item-git-status='modified'] {
    --trees-item-git-status-color: var(--trees-git-modified-color);
  }

  [data-item-git-status='renamed'] {
    --trees-item-git-status-color: var(--trees-git-renamed-color);
  }

  [data-item-git-status='untracked'] {
    --trees-item-git-status-color: var(--trees-git-untracked-color);
  }

  /* Drag and drop */
  [data-item-drag-target='true'] {
    background-color: var(--trees-selected-bg);
  }

  [data-item-dragging='true'] {
    opacity: 0.5;
  }

  /* Lock icon for locked paths (sibling of content) */
  [data-item-section='lock'] {
    flex: 0 0 auto;
    margin-left: auto;
    display: flex;
    align-items: center;
    color: var(--trees-fg-muted);
  }
  [data-item-section='lock'] svg {
    display: block;
  }

  [data-type='header-slot'] {
    display: block;
    flex: 0 0 auto;
  }

  [data-type='context-menu-wash'] {
    position: absolute;
    inset: 0;
    z-index: 3;
    background-color: transparent;
    touch-action: none;
  }

  [data-type='context-menu-anchor'] {
    position: absolute;
    top: 0;
    right: var(--trees-context-menu-trigger-inline-offset);
    z-index: 4;
    display: none;
    align-items: center;

    &[data-visible='true'] {
      display: flex;
    }
  }

  /* Hide the floating trigger while the scroll container is actively moving.
   * The anchor is positioned against the root, not the scroll content, so its
   * \`top\` follows the row via a React state update — one frame behind the
   * compositor. That delay is visible as the trigger hovering over the wrong
   * row during the first frame of a scroll. The \`data-is-scrolling\` flag on
   * the root is flipped synchronously on \`wheel\`/\`touchmove\`/\`keydown\` before
   * the compositor commits the next paint, so this selector hides the anchor
   * in the same frame the scroll begins. */
  [data-file-tree-virtualized-root='true'][data-is-scrolling]
    [data-type='context-menu-anchor'] {
    display: none;
  }

  [data-type='context-menu-anchor'] > slot[name='context-menu'] {
    display: block;
    width: 0;
    min-width: 0;
    flex: 0 0 0;
    overflow: visible;
  }

  /* Single floating context menu trigger */
  [data-type='context-menu-trigger'] {
    all: unset;
    align-items: center;
    justify-content: center;
    width: var(--trees-action-lane-width);
    color: var(--trees-fg-muted);
    fill: currentColor;
    cursor: pointer;
    font-family: var(--trees-font-family);
    font-size: var(--trees-font-size);
    border-top-right-radius: var(--trees-border-radius);
    border-bottom-right-radius: var(--trees-border-radius);
    margin: var(--trees-focus-ring-width);
    height: calc(var(--trees-row-height) - var(--trees-focus-ring-width) * 2);
    border-width: 0;
    transition: color 120ms ease;

    display: flex;
  }

  [data-type='context-menu-trigger']:hover,
  [data-type='context-menu-trigger'][aria-expanded='true'] {
    color: var(--trees-fg);
  }

  /** @pierre/truncate css here, manually copy pasted for now */
  [data-truncate-container] {
    /* CUSTOM TO TREES, TO SUPPORT THE OUTLINE */
    margin-top: -1px;
    margin-bottom: -1px;

    /* Width of the fade from default marker to text */
    --truncate-internal-marker-fade-width: var(
      --truncate-marker-fade-width,
      2px
    );
    /* Width of the solid color between the fade from the default marker to the text */
    --truncate-internal-marker-gap: var(--truncate-marker-gap, 0px);
    /* Opacity of the marker 'color' property, not of the element itself */
    --truncate-internal-marker-opacity: var(--truncate-marker-opacity, 50%);
    /* Opacity of the marker 'color' property specifically for the middle truncate, not opacity of the element itself */
    --truncate-internal-middle-marker-opacity: var(
      --truncate-middle-marker-opacity,
      80%
    );
    /* Background color of the default marker */
    --truncate-internal-marker-background-color: var(
      --truncate-marker-background-color,
      light-dark(white, black)
    );
    --truncate-internal-marker-background-overlay-color: var(
      --truncate-marker-background-overlay-color,
      transparent
    );
    --truncate-internal-marker-block-inset: var(
      --truncate-marker-block-inset,
      0px
    );
    /* Duration of the fade out animation for the marker */
    --truncate-internal-marker-fade-out-duration: var(
      --truncate-marker-fade-out-duration,
      0ms
    );
    /* Duration of the fade in animation for the marker */
    --truncate-internal-marker-fade-in-duration: var(
      --truncate-marker-fade-in-duration,
      100ms
    );

    /* FADE Variant specifics */
    --truncate-internal-fade-marker-color: var(
      --truncate-fade-marker-color,
      #000
    );
    --truncate-internal-fade-marker-width: var(
      --truncate-fade-marker-width,
      0.2lh
    );

    /*
    In some special cases people might be adding spacing in other ways
    that would benefit from being able to override this, however the container
    query below can't use this and would need to be redeclared with the overridden
    value. It's a bad time, but better than nothing.
    */
    --truncate-internal-single-line-height: 1lh;

    height: var(--truncate-internal-single-line-height);
    min-width: 0;
    overflow: hidden;
  }

  [data-truncate-marker] {
    display: flex;
    position: absolute;
    height: var(--truncate-internal-single-line-height);
    padding-block: var(--truncate-internal-marker-block-inset);
    box-sizing: border-box;
    align-items: center;
    background-clip: content-box;
    z-index: 2;
    color: color-mix(
      in srgb,
      currentColor var(--truncate-internal-marker-opacity),
      transparent
    );

    /* Core trick for hiding the marker until overflow occurs */
    opacity: 0;
    transition: opacity var(--truncate-internal-marker-fade-out-duration)
      ease-in-out;
  }

  @container measure (height > 1lh) {
    [data-truncate-marker] {
      opacity: 1;
      transition: opacity var(--truncate-internal-marker-fade-in-duration)
        ease-in-out;
    }
  }

  [data-truncate-grid] {
    display: grid;
    position: relative;
  }

  [data-truncate-content='visible'] {
    white-space: nowrap;
  }

  [data-truncate-content='overflow'] {
    opacity: 0;
    pointer-events: none;
    -webkit-user-select: none;
            user-select: none;
    word-break: break-all;
    margin-top: calc(-1 * var(--truncate-internal-single-line-height));
  }

  [data-truncate-marker-cell] {
    container: measure / size;
    overflow: visible;
    -webkit-user-select: none;
            user-select: none;
    pointer-events: none;
  }

  [data-truncate-container='truncate'] {
    & [data-truncate-grid] {
      grid-template-columns: minmax(0, max-content) 0;
    }
    & [data-truncate-marker] {
      right: 0;
    }
    & [data-truncate-fade] {
      margin-right: calc(-2 * var(--truncate-internal-fade-marker-width));
    }
  }

  [data-truncate-container='fruncate'] {
    & [data-truncate-grid] {
      grid-template-columns: 0 minmax(0, max-content) auto;
    }
    & [data-truncate-content] {
      direction: rtl;
    }
    & [data-truncate-content] > span {
      unicode-bidi: plaintext;
    }
    & [data-truncate-fade] {
      margin-left: calc(-2 * var(--truncate-internal-fade-marker-width));
    }
  }

  [data-truncate-variant='default'] {
    & [data-truncate-marker] {
      background-color: var(--truncate-internal-marker-background-color);
      background-image: linear-gradient(
        var(--truncate-internal-marker-background-overlay-color),
        var(--truncate-internal-marker-background-overlay-color)
      );
    }
    & [data-truncate-marker]::after,
    & [data-truncate-marker]::before {
      content: '';
      position: absolute;
      width: calc(
        var(--truncate-internal-marker-fade-width) +
          var(--truncate-internal-marker-gap)
      );
      inset-block-start: var(--truncate-internal-marker-block-inset);
      height: max(
        0px,
        calc(
          var(--truncate-internal-single-line-height) -
            var(--truncate-internal-marker-block-inset) * 2
        )
      );
      background-color: var(--truncate-internal-marker-background-color);
      background-image: linear-gradient(
        var(--truncate-internal-marker-background-overlay-color),
        var(--truncate-internal-marker-background-overlay-color)
      );
      mask-image: linear-gradient(
        var(--truncate-internal-fade-dir),
        #000 0%,
        #000 var(--truncate-internal-marker-gap),
        transparent 100%
      );
    }
    & [data-truncate-marker]::after {
      --truncate-internal-fade-dir: to right;
      right: calc(
        -1 *
          (
            var(--truncate-internal-marker-fade-width) +
              var(--truncate-internal-marker-gap)
          )
      );
    }
    & [data-truncate-marker]::before {
      --truncate-internal-fade-dir: to left;
      left: calc(
        -1 *
          (
            var(--truncate-internal-marker-fade-width) +
              var(--truncate-internal-marker-gap)
          )
      );
    }
  }

  [data-truncate-variant='fade'] {
    & [data-truncate-marker] {
      background: transparent;
    }
  }

  [data-truncate-fade] {
    box-shadow:
      0 0 calc(var(--truncate-internal-fade-marker-width) / 2)
        var(--truncate-internal-fade-marker-color),
      0 0 var(--truncate-internal-fade-marker-width)
        var(--truncate-internal-fade-marker-color);
    width: calc(var(--truncate-internal-fade-marker-width) * 2);
    height: calc(
      var(--truncate-internal-single-line-height) -
        (var(--truncate-internal-fade-marker-width) * 2)
    );
    margin: var(--truncate-internal-fade-marker-width) 0;
  }

  [data-truncate-group-container='middle'] {
    & [data-truncate-container] {
      --truncate-marker-opacity: var(--truncate-internal-middle-marker-opacity);
    }

    display: flex;
    min-width: 0;

    & > div {
      min-width: 0;
    }

    & > div[data-truncate-segment-priority='1'] {
      flex: 0 1 max-content;
    }
    & > div[data-truncate-segment-priority='2'] {
      flex: 0 999999 max-content;
    }
  }
}
`;function K7(X){return`@layer base, unsafe;
@layer base {
  ${X}
}`}function j9(X){return`@layer base, unsafe;
@layer unsafe {
  ${X}
}`}var _9=new WeakMap;function VX(X){let Q=_9.get(X);if(Q!=null)return Q;let Z=document.createElement("div");Z.setAttribute(W9,"true");let Y=document.createElement("div");Y.style.position="relative",Y.style.height="200%",Z.appendChild(Y),X.appendChild(Z);let J=Math.max(Z.offsetWidth-Z.clientWidth,0);return Z.remove(),_9.set(X,J),J}function F9(X,Q){if(!X.isConnected)return;let Z=VX(Q);if(Z==null)return;let Y=Q.querySelector(`style[${i7}]`),J=Y instanceof HTMLStyleElement?Y:document.createElement("style");if(!(Y instanceof HTMLStyleElement))J.setAttribute(i7,""),Q.appendChild(J);J.textContent=`:host { ${G9}: ${Z}px; }`}var M7;function RX(X){if(typeof CSSStyleSheet<"u"&&typeof CSSStyleSheet.prototype.replaceSync==="function"&&"adoptedStyleSheets"in X){if(M7==null)M7=new CSSStyleSheet,M7.replaceSync(K7(r7));let Q=!1;try{X.adoptedStyleSheets=[M7],Q=!0}catch{}if(Q){X.querySelector(`style[${f6}]`)?.remove();return}}if(X.querySelector(`style[${f6}]`)==null){let Q=document.createElement("style");Q.setAttribute(f6,""),Q.textContent=K7(r7),X.prepend(Q)}}function H7(X,Q){EX(X,Q),RX(Q),F9(X,Q)}function EX(X,Q){let Z=X.querySelector('template[shadowrootmode="open"], template[data-file-tree-shadowrootmode="open"]');if(!(Z instanceof HTMLTemplateElement))return;if(Q.childNodes.length>0)return;if(Q.appendChild(Z.content.cloneNode(!0)),Z.hasAttribute("shadowrootmode"))Z.remove()}if(typeof HTMLElement<"u"&&customElements.get(D5)==null){class X extends HTMLElement{constructor(){super()}connectedCallback(){let Q=this.shadowRoot??this.attachShadow({mode:"open"});H7(this,Q)}}if(customElements.define(D5,X),typeof document<"u")for(let Q of Array.from(document.querySelectorAll(D5))){if(!(Q instanceof HTMLElement))continue;H7(Q,Q.shadowRoot??Q.attachShadow({mode:"open"}))}}var V9=!0;var R9=128;function h5(){return{childIdByNameId:new Map,childIds:[],childPositionById:new Map,childVisibleChunkSums:null,totalChildSubtreeNodeCount:0,totalChildVisibleSubtreeCount:0}}function a7(){return{childIdByNameId:null,childIds:[],childPositionById:null,childVisibleChunkSums:null,totalChildSubtreeNodeCount:0,totalChildVisibleSubtreeCount:0}}function T5(X,Q){if(Q.childIdByNameId!=null)return Q.childIdByNameId;let Z=new Map;for(let Y of Q.childIds){let J=X[Y];if(J!=null)Z.set(J.nameId,Y)}return Q.childIdByNameId=Z,Z}function q6(X){if(X.childPositionById!=null)return X.childPositionById;let Q=new Map;for(let Z=0;Z<X.childIds.length;Z++){let Y=X.childIds[Z];if(Y!=null)Q.set(Y,Z)}return X.childPositionById=Q,Q}function $6(X,Q){if(X.childPositionById!=null)X.childPositionById.set(Q,X.childIds.length);X.childIds.push(Q)}function n7(X,Q){if(X.childPositionById==null)return;for(let Z=Q;Z<X.childIds.length;Z++){let Y=X.childIds[Z];if(Y!=null)X.childPositionById.set(Y,Z)}}function p5(X,Q){let Z=0,Y=0;for(let J of Q.childIds){let W=X[J];if(W==null)continue;Z+=W.subtreeNodeCount,Y+=W.visibleSubtreeCount}Q.totalChildSubtreeNodeCount=Z,Q.totalChildVisibleSubtreeCount=Y,c5(X,Q)}function A7(X,Q,Z,Y){if(X.totalChildSubtreeNodeCount+=Z,X.totalChildVisibleSubtreeCount+=Y,X.childVisibleChunkSums==null||Y===0)return;let J=q6(X).get(Q);if(J===void 0)return;let W=J>>5;X.childVisibleChunkSums[W]+=Y}function L7(X,Q,Z){let Y=Q.childVisibleChunkSums;if(Y!=null){let W=Z,G=0;for(let q of Y){if(W<q){let U=DX(X,Q,G,W);return{...U,childVisibleIndex:Z-U.localVisibleIndex}}W-=q,G+=32}throw Error(`Visible child index ${String(Z)} is out of range`)}let J=Z;for(let W=0;W<Q.childIds.length;W++){let G=Q.childIds[W];if(G==null)continue;let q=X[G];if(q==null)continue;if(J<q.visibleSubtreeCount)return{childIndex:W,childVisibleIndex:Z-J,localVisibleIndex:J};J-=q.visibleSubtreeCount}throw Error(`Visible child index ${String(Z)} is out of range`)}function E9(X,Q,Z){let Y=0,J=Q.childVisibleChunkSums,W=0;if(J!=null){let G=Z>>5;for(let q=0;q<G;q+=1)Y+=J[q]??0;W=G<<5}for(let G=W;G<Z;G+=1){let q=Q.childIds[G];if(q==null)continue;let U=X[q];if(U==null)continue;Y+=U.visibleSubtreeCount}return Y}function c5(X,Q){if(Q.childIds.length<128){Q.childVisibleChunkSums=null;return}let Z=Math.ceil(Q.childIds.length/32),Y=new Int32Array(Z);for(let J=0;J<Q.childIds.length;J++){let W=Q.childIds[J];if(W==null)continue;let G=X[W];if(G==null)continue;Y[J>>5]+=G.visibleSubtreeCount}Q.childVisibleChunkSums=Y}function DX(X,Q,Z,Y){let J=Math.min(Q.childIds.length,Z+32),W=Y;for(let G=Z;G<J;G++){let q=Q.childIds[G];if(q==null)continue;let U=X[q];if(U==null)continue;if(W<U.visibleSubtreeCount)return{childIndex:G,localVisibleIndex:W};W-=U.visibleSubtreeCount}throw Error(`Visible child index ${String(Y)} is out of range`)}var D9=0,d4=1,q5=1,f4=2,l5=4;function u4(X,Q,Z=0){return X<<4|Z<<3|Q}function s4(X){return X.depthAndFlags>>>4}function y6(X){return(X.depthAndFlags&8)>>3}function y(X){return(X.depthAndFlags&8)!==0}function k9(X){return X.depthAndFlags&7}function _4(X,Q){return(k9(X)&Q)!==0}function U6(X,Q){X.depthAndFlags|=Q}function T9(X,Q){X.depthAndFlags=u4(Q,k9(X),y6(X))}var w9=Symbol("benchmarkInstrumentation");function N9(X,Q){if(Q==null)return X;return Object.defineProperty(X,w9,{configurable:!0,enumerable:!1,value:Q,writable:!1}),X}function x6(X){if(X==null)return null;return X[w9]??null}function S(X,Q,Z){if(X==null)return Z();return X.measurePhase(Q,Z)}function z6(X,Q,Z){if(!Number.isFinite(Z)||X==null)return;X.setCounter(Q,Z)}function C9(X){return X>=48&&X<=57}function kX(X){let Q=[],Z=0,Y=0;while(Y<X.length){while(Y<X.length&&!C9(X.charCodeAt(Y)))Y+=1;if(Y>=X.length)break;if(Y>Z)Q.push(X.slice(Z,Y));let J=0;while(Y<X.length&&C9(X.charCodeAt(Y)))J=J*10+(X.charCodeAt(Y)-48),Y+=1;Q.push(J),Z=Y}if(Z<X.length||Q.length===0)Q.push(X.slice(Z));return Q}function d5(X){let Q=X.toLowerCase();return{lowerValue:Q,tokens:kX(Q)}}function TX(X,Q){let Z=Math.min(X.length,Q.length);for(let Y=0;Y<Z;Y++){let J=X[Y],W=Q[Y];if(J===W)continue;if(typeof J==="number"&&typeof W==="number")return J<W?-1:1;let G=String(J),q=String(W);if(G!==q)return G<q?-1:1}if(X.length!==Q.length)return X.length<Q.length?-1:1;return 0}function g6(X,Q){if(X.tokens.length===1&&Q.tokens.length===1&&typeof X.tokens[0]==="string"&&typeof Q.tokens[0]==="string"){if(X.lowerValue===Q.lowerValue)return 0;return X.lowerValue<Q.lowerValue?-1:1}let Z=TX(X.tokens,Q.tokens);if(Z!==0)return Z;if(X.lowerValue!==Q.lowerValue)return X.lowerValue<Q.lowerValue?-1:1;return 0}function v9(X,Q,Z){let Y=g6(Z(X),Z(Q));if(Y!==0)return Y;if(X===Q)return 0;return X<Q?-1:1}function wX(X,Q){return v9(X,Q,d5)}function O7(X,Q){if(Q!==X.segments.length-1)return d4;return X.isDirectory?d4:D9}function NX(X,Q){let Z=Math.min(X.segments.length,Q.segments.length);for(let Y=0;Y<Z;Y++){let J=X.segments[Y],W=Q.segments[Y];if(J===W)continue;let G=O7(X,Y);if(G!==O7(Q,Y))return G===d4?-1:1;return wX(J,W)}if(X.segments.length!==Q.segments.length)return X.segments.length<Q.segments.length?-1:1;if(X.isDirectory===Q.isDirectory)return 0;return X.isDirectory?-1:1}function b9(X,Q){return NX(X,Q)}function S9(X,Q,Z){let Y=(W)=>{let G=Z.get(W);if(G!=null)return G;let q=d5(W);return Z.set(W,q),q},J=Math.min(X.segments.length,Q.segments.length);for(let W=0;W<J;W++){let G=X.segments[W],q=Q.segments[W];if(G===q)continue;let U=O7(X,W);if(U!==O7(Q,W))return U===d4?-1:1;return v9(G,q,Y)}if(X.segments.length!==Q.segments.length)return X.segments.length<Q.segments.length?-1:1;if(X.isDirectory===Q.isDirectory)return 0;return X.isDirectory?-1:1}function I6(X,Q){let Z=X.sortKeyById[Q];if(Z!==void 0)return Z;let Y=X.valueById[Q],J=d5(Y);return X.sortKeyById[Q]=J,J}function t7(X={}){return{flattenEmptyDirectories:X.flattenEmptyDirectories!==!1,sort:X.sort??"default"}}function P9(X){let Q=X.length>0&&X.charCodeAt(X.length-1)===47,Z=Q?X.length-1:X.length,Y=[],J=0;for(let W=0;W<Z;W++){if(X.charCodeAt(W)!==47)continue;Y.push(X.slice(J,W)),J=W+1}return Y.push(X.slice(J,Z)),{hasTrailingSlash:Q,segments:Y}}function s5(X){let{hasTrailingSlash:Q,segments:Z}=P9(X);return{basename:Z[Z.length-1]??"",isDirectory:Q,path:X,segments:Z}}function B7(X){if(X.length===0)return{requiresDirectory:!1,segments:[]};let{hasTrailingSlash:Q,segments:Z}=P9(X);return{requiresDirectory:Q,segments:Z}}var e7="";function j7(){let X=new Map;return X.set(e7,0),{idByValue:X,valueById:[e7],sortKeyById:[d5(e7)]}}function Y5(X,Q){let Z=X.idByValue.get(Q);if(Z!==void 0)return Z;let Y=X.valueById.length;return X.idByValue.set(Q,Y),X.valueById.push(Q),Y}function a4(X,Q){let Z=X.valueById[Q];if(Z===void 0)throw Error(`Unknown segment ID: ${String(Q)}`);return Z}var X8=Symbol("pathStorePreparedInputKind");function x9(X,Q){return X[X8]=Q,X}function f9(X){return{basename:X.basename,depth:X.segments.length,isDirectory:X.isDirectory,path:X.path,segments:X.segments}}function g9(X,Q,Z){if(Z==="default")return b9(X,Q);return Z(f9(X),f9(Q))}function CX(){return{depthAndFlags:u4(0,q5|f4,d4),nameId:0,parentId:0,subtreeNodeCount:1,visibleSubtreeCount:1}}function vX(X,Q){let Z=Math.min(X.length,Q.length);for(let Y=0;Y<Z;Y++)if(X[Y]!==Q[Y])return Y;return Z}function y9(X){return X.isDirectory?X.segments.length:X.segments.length-1}function bX(X){return Array.isArray(X)&&X.every((Q)=>Q!=null&&typeof Q==="object"&&typeof Q.path==="string"&&Array.isArray(Q.segments)&&typeof Q.basename==="string"&&typeof Q.isDirectory==="boolean")}function SX(X){return Array.isArray(X)&&X.every((Q)=>typeof Q==="string")}function I9(X,Q={}){return _7(X,Q).map((Z)=>Z.path)}function m9(X,Q={}){let Z=_7(X,Q);return x9({paths:Z.map((Y)=>Y.path),preparedPaths:Z},"prepared")}function u9(X){let Q=X.length,Z=!1;for(let Y=0;Y<Q;Y+=1){let J=X[Y];if(J.length>0&&J.charCodeAt(J.length-1)===47){Z=!0;break}}return x9({paths:X,presortedPaths:X,presortedPathsContainDirectories:Z},"presorted")}function h9(X){let Q=X,Z=Q.preparedPaths;if(Q[X8]==="prepared"&&Z!=null)return Z;if(!bX(Z))throw Error("preparedInput must come from PathStore.prepareInput()");return Z}function p9(X){let Q=X;if(Q[X8]==="presorted"&&Q.presortedPaths!=null)return Q.presortedPaths;return SX(Q.presortedPaths)?Q.presortedPaths:null}function c9(X){let Q=X;return typeof Q.presortedPathsContainDirectories==="boolean"?Q.presortedPathsContainDirectories:null}function _7(X,Q={}){let Z=t7(Q),Y=x6(Q);z6(Y,"workload.inputFiles",X.length);let J=S(Y,"store.preparePathEntries.parse",()=>X.map((W)=>s5(W)));return S(Y,"store.preparePathEntries.sort",()=>J.sort((W,G)=>g9(W,G,Z.sort))),J}var F7=class{directories=new Map;directoryStack=[0];presortedDirectoryNodeIds=[];initialExpandedPathSet;createdDirectoriesAllExpanded=!1;createdDirectoryCount=0;lastPreparedPath=null;nodes=[CX()];options;instrumentation;segmentSortKeyCache=new Map;segmentTable=j7();hasDeferredDirectoryIndexes=!1;constructor(X={}){this.instrumentation=x6(X),this.options=t7(X);let Q=X.initialExpandedPaths??null;if(Q==null||Q.length===0)this.initialExpandedPathSet=null;else{let Z=new Set,Y=Q.length;for(let J=0;J<Y;J+=1){let W=Q[J],G=W.length;Z.add(G>0&&W.charCodeAt(G-1)===47?W.slice(0,G-1):W)}this.initialExpandedPathSet=Z,this.createdDirectoriesAllExpanded=!0}this.directories.set(0,h5())}appendPaths(X){return S(this.instrumentation,"store.builder.appendPaths.parse",()=>this.appendPreparedPaths(X.map((Q)=>s5(Q))))}appendPreparedPaths(X,Q=!0){return this.createdDirectoriesAllExpanded=!1,S(this.instrumentation,"store.builder.appendPreparedPaths",()=>{for(let Z of X)this.appendPreparedPath(Z,Q)}),this}appendPresortedPaths(X,Q=null){return S(this.instrumentation,"store.builder.appendPresortedPaths",()=>{if(Q===!1){this.appendPresortedFilePaths(X);return}this.createdDirectoriesAllExpanded=!1;let Z=null,Y=0,J=this.nodes,W=this.segmentTable,G=W.idByValue,q=W.valueById,U=this.directoryStack,A=0,M="",O=0;for(let z of X){if(Z===z)throw Error(`Duplicate path: "${z}"`);let j=z.length>0&&z.charCodeAt(z.length-1)===47,B=j?z.length-1:z.length,R=0,D=0;if(Z!=null)if(M.length>0&&z.length>M.length&&z.startsWith(M))R=O,D=M.length;else{let F=Math.min(B,Z.length),V=!0;for(let k=0;k<F;k++){let P=z.charCodeAt(k);if(P!==Z.charCodeAt(k)){V=!1;break}if(P===47)R++,D=k+1}if(V&&j&&F===B&&Z.length>B&&Z.charCodeAt(B)===47)R++,D=B+1}A=R,Y=R;let b=D,w=z.indexOf("/",b);while(w>=0&&w<B){let F=U[A];if(F===void 0)throw Error("Directory stack underflow while building the path store");Y++;let V=z.slice(b,w),k=G.get(V);if(k===void 0)k=q.length,G.set(V,k),q.push(V);let P=J.length;J.push({depthAndFlags:u4(Y,0,d4),nameId:k,parentId:F,subtreeNodeCount:1,visibleSubtreeCount:1}),this.recordCreatedDirectoryPath(z.slice(0,w)),A++,U[A]=P,b=w+1,w=z.indexOf("/",b)}if(j){if(b<B){let V=U[A];if(V===void 0)throw Error(`Unable to resolve directory parent for "${z}"`);Y++;let k=z.slice(b,B),P=G.get(k);if(P===void 0)P=q.length,G.set(k,P),q.push(k);let h=J.length;J.push({depthAndFlags:u4(Y,0,d4),nameId:P,parentId:V,subtreeNodeCount:1,visibleSubtreeCount:1}),A++,U[A]=h}let F=U[A];if(F===void 0)throw Error(`Unable to resolve directory node for "${z}"`);this.promoteDirectoryToExplicit(F,z)}else{let F=U[A];if(F===void 0)throw Error(`Unable to resolve file parent for "${z}"`);let V=z.slice(b),k=G.get(V);if(k===void 0)k=q.length,G.set(V,k),q.push(V);J.push({depthAndFlags:u4(Y+1,0),nameId:k,parentId:F,subtreeNodeCount:1,visibleSubtreeCount:1})}if(b!==M.length)M=z.substring(0,b),O=Y;Z=z}if(U.length=A+1,Z!=null)this.lastPreparedPath=s5(Z);this.hasDeferredDirectoryIndexes=!0}),this}appendPresortedFilePaths(X){let Q=null,Z=0,Y=this.nodes,J=this.segmentTable,W=J.idByValue,G=J.valueById,q=this.directoryStack,U=0,A="",M=0;for(let O of X){if(Q===O)throw Error(`Duplicate path: "${O}"`);let z=O.length,j=0,B=0;if(Q!=null)if(A.length>0&&O.length>A.length&&O.startsWith(A))j=M,B=A.length;else{let V=Math.min(z,Q.length);for(let k=0;k<V;k++){let P=O.charCodeAt(k);if(P!==Q.charCodeAt(k))break;if(P===47)j++,B=k+1}}U=j,Z=j;let R=B,D=O.indexOf("/",R);while(D>=0){let V=q[U];if(V===void 0)throw Error("Directory stack underflow while building the path store");Z++;let k=O.slice(R,D),P=W.get(k);if(P===void 0)P=G.length,W.set(k,P),G.push(k);let h=Y.length;Y.push({depthAndFlags:u4(Z,0,d4),nameId:P,parentId:V,subtreeNodeCount:1,visibleSubtreeCount:1}),this.recordCreatedDirectoryPath(O.slice(0,D)),this.presortedDirectoryNodeIds.push(h),U++,q[U]=h,R=D+1,D=O.indexOf("/",R)}let b=q[U];if(b===void 0)throw Error(`Unable to resolve file parent for "${O}"`);let w=O.slice(R),F=W.get(w);if(F===void 0)F=G.length,W.set(w,F),G.push(w);if(Y.push({depthAndFlags:u4(Z+1,0),nameId:F,parentId:b,subtreeNodeCount:1,visibleSubtreeCount:1}),R!==A.length)A=O.substring(0,R),M=Z;Q=O}if(q.length=U+1,Q!=null)this.lastPreparedPath=s5(Q);this.hasDeferredDirectoryIndexes=!0}finish(X={}){let Q=X.skipSubtreeCountPass===!0;if(this.hasDeferredDirectoryIndexes)S(this.instrumentation,"store.builder.buildDirectoryIndexes",()=>this.buildPresortedFinish(Q)),this.hasDeferredDirectoryIndexes=!1;else if(!Q)S(this.instrumentation,"store.builder.computeSubtreeCounts",()=>this.computeSubtreeCounts(0));return{directories:this.directories,nodes:this.nodes,options:this.options,rootId:0,segmentTable:this.segmentTable,presortedDirectoryNodeIds:this.presortedDirectoryNodeIds.length>0?this.presortedDirectoryNodeIds:null}}didMatchAllInitialExpandedPaths(){return this.createdDirectoriesAllExpanded&&this.initialExpandedPathSet!=null&&this.createdDirectoryCount===this.initialExpandedPathSet.size}appendPreparedPath(X,Q){if(this.hasDeferredDirectoryIndexes)this.buildDirectoryIndexes(),this.hasDeferredDirectoryIndexes=!1;if(this.lastPreparedPath!=null){if(X.path===this.lastPreparedPath.path)throw Error(`Duplicate path: "${X.path}"`);if(Q){if((this.options.sort==="default"?S9(this.lastPreparedPath,X,this.segmentSortKeyCache):g9(this.lastPreparedPath,X,this.options.sort))>0)throw Error(`Builder input must be sorted before appendPaths(): "${X.path}"`)}}let Z=this.lastPreparedPath,Y=y9(X),J=Z==null?0:y9(Z),W=Z==null?0:vX(Z.segments,X.segments),G=Math.min(W,Y,J);this.directoryStack.length=G+1;for(let U=G;U<Y;U++){let A=this.directoryStack[this.directoryStack.length-1];if(A===void 0)throw Error("Directory stack underflow while building the path store");let M=Q?this.getOrCreateDirectoryChild(A,X.segments[U]):this.createDirectoryChild(A,X.segments[U]);this.directoryStack.push(M)}if(X.isDirectory){let U=this.directoryStack[this.directoryStack.length-1];if(U===void 0)throw Error(`Unable to resolve directory node for "${X.path}"`);this.promoteDirectoryToExplicit(U,X.path),this.lastPreparedPath=X;return}let q=this.directoryStack[this.directoryStack.length-1];if(q===void 0)throw Error(`Unable to resolve file parent for "${X.path}"`);if(Q)this.createFileChild(q,X.basename,X.path);else this.createFileChildUnchecked(q,X.basename);this.lastPreparedPath=X}recordCreatedDirectoryPath(X){if(!this.createdDirectoriesAllExpanded||this.initialExpandedPathSet==null)return;if(this.createdDirectoryCount+=1,!this.initialExpandedPathSet.has(X))this.createdDirectoriesAllExpanded=!1}createFileChild(X,Q,Z){let Y=Y5(this.segmentTable,Q),J=this.getDirectoryIndex(X),W=J.childIdByNameId;if(W!=null){if(W.get(Y)!==void 0)throw Error(`Path collides with an existing entry: "${Z}"`)}let G=this.nodes[X];if(G===void 0)throw Error(`Unknown parent node ID: ${String(X)}`);let q=this.nodes.length;if(this.nodes.push({depthAndFlags:u4(s4(G)+1,0),nameId:Y,parentId:X,subtreeNodeCount:1,visibleSubtreeCount:1}),W!=null)W.set(Y,q);return $6(J,q),q}createFileChildUnchecked(X,Q){let Z=Y5(this.segmentTable,Q),Y=this.getDirectoryIndex(X),J=this.nodes[X];if(J===void 0)throw Error(`Unknown parent node ID: ${String(X)}`);let W=this.nodes.length;if(this.nodes.push({depthAndFlags:u4(s4(J)+1,0),nameId:Z,parentId:X,subtreeNodeCount:1,visibleSubtreeCount:1}),Y.childIdByNameId!=null)Y.childIdByNameId.set(Z,W);return $6(Y,W),W}getOrCreateDirectoryChild(X,Q){let Z=Y5(this.segmentTable,Q),Y=this.getDirectoryIndex(X);if(Y.childIdByNameId!=null){let G=Y.childIdByNameId.get(Z);if(G!==void 0){let q=this.nodes[G];if(q!=null&&!y(q))throw Error(`Path collides with an existing file while creating directory "${Q}"`);return G}}let J=this.nodes[X];if(J===void 0)throw Error(`Unknown parent node ID: ${String(X)}`);let W=this.nodes.length;if(this.nodes.push({depthAndFlags:u4(s4(J)+1,0,d4),nameId:Z,parentId:X,subtreeNodeCount:1,visibleSubtreeCount:1}),Y.childIdByNameId!=null)Y.childIdByNameId.set(Z,W);return $6(Y,W),this.directories.set(W,h5()),W}createDirectoryChild(X,Q){let Z=Y5(this.segmentTable,Q),Y=this.getDirectoryIndex(X),J=this.nodes[X];if(J===void 0)throw Error(`Unknown parent node ID: ${String(X)}`);let W=this.nodes.length;if(this.nodes.push({depthAndFlags:u4(s4(J)+1,0,d4),nameId:Z,parentId:X,subtreeNodeCount:1,visibleSubtreeCount:1}),Y.childIdByNameId!=null)Y.childIdByNameId.set(Z,W);return $6(Y,W),this.directories.set(W,h5()),W}promoteDirectoryToExplicit(X,Q){let Z=this.nodes[X];if(Z===void 0)throw Error(`Unknown directory node ID: ${String(X)}`);if(!y(Z))throw Error(`Path is not a directory: "${Q}"`);if(_4(Z,q5))throw Error(`Duplicate path: "${Q}"`);U6(Z,q5)}getDirectoryIndex(X){let Q=this.directories.get(X);if(Q!==void 0)return Q;throw Error(`Unknown directory child index for node ${String(X)}`)}buildPresortedFinish(X){let Q=this.nodes,Z=this.directories;Z.set(0,a7());let Y=-1,J=null;for(let W=1;W<Q.length;W++){let G=Q[W];if(G==null)continue;if(y(G)){let U=a7();Z.set(W,U),Y=W,J=U}let q;if(G.parentId===Y)q=J;else q=Z.get(G.parentId),Y=G.parentId,J=q??null;if(q!=null)q.childIds.push(W)}if(X)return;for(let W=Q.length-1;W>=1;W--){let G=Q[W];if(G==null)continue;let q=Q[G.parentId];if(q!=null)q.subtreeNodeCount+=G.subtreeNodeCount,q.visibleSubtreeCount+=G.visibleSubtreeCount}}buildDirectoryIndexes(){let X=this.nodes;for(let Q=1;Q<X.length;Q++){let Z=X[Q];if(Z==null)continue;if(y(Z))this.directories.set(Q,h5());let Y=this.directories.get(Z.parentId);if(Y!=null){if(Y.childIdByNameId!=null)Y.childIdByNameId.set(Z.nameId,Q);$6(Y,Q)}}}computeSubtreeCounts(X){let Q=this.nodes[X];if(Q===void 0)throw Error(`Unknown node ID: ${String(X)}`);if(!y(Q))return Q.subtreeNodeCount=1,Q.visibleSubtreeCount=1,1;let Z=this.getDirectoryIndex(X),Y=1;for(let J of Z.childIds)Y+=this.computeSubtreeCounts(J);return p5(this.nodes,Z),Q.subtreeNodeCount=Y,Q.visibleSubtreeCount=Y,Y}};function l9(X,Q="closed",Z=null){let Y=PX(Q);return{activeNodeCount:X.nodes.length-1,collapsedDirectoryIds:new Set,collapseNewDirectoriesByDefault:!1,defaultExpansion:Y,directoriesOpenByDefault:Y==="open",hasCollapsedDirectoryOverrides:!1,directoryLoadInfoById:new Map,expandedDirectoryIds:new Set,instrumentation:Z,listeners:new Map,pathCacheByNodeId:new Map([[X.rootId,{path:"",version:0}]]),pathCacheVersion:0,snapshot:X,transactionStack:[]}}function d9(){return{affectedAncestorIds:new Set,affectedNodeIds:new Set,events:[]}}function PX(X){if(typeof X!=="number")return X;if(!Number.isInteger(X)||X<0)throw Error(`initialExpansion must be "open", "closed", or a non-negative integer depth. Received: ${String(X)}`);return X}function s9(X,Q){if(_4(Q,f4))return!0;if(X.defaultExpansion==="open")return!0;if(X.defaultExpansion==="closed")return!1;return s4(Q)<=X.defaultExpansion}function y4(X,Q,Z=X.snapshot.nodes[Q]){if(Z==null||!y(Z))return!1;if(X.directoriesOpenByDefault&&!X.hasCollapsedDirectoryOverrides)return!0;if(X.collapsedDirectoryIds.has(Q))return!1;if(X.expandedDirectoryIds.has(Q))return!0;return s9(X,Z)}function w5(X,Q,Z,Y=X.snapshot.nodes[Q]){if(Y==null||!y(Y))return;let J=s9(X,Y);if(Z){if(J){X.collapsedDirectoryIds.delete(Q),X.hasCollapsedDirectoryOverrides=X.collapsedDirectoryIds.size>0;return}X.expandedDirectoryIds.add(Q);return}if(J){X.collapsedDirectoryIds.add(Q),X.hasCollapsedDirectoryOverrides=!0;return}X.expandedDirectoryIds.delete(Q)}function i9(X,Q){let Z=X.directoryLoadInfoById.get(Q);if(Z!=null)return Z;let Y={activeAttemptId:null,errorMessage:null,nextAttemptId:1,state:"loaded"};return X.directoryLoadInfoById.set(Q,Y),Y}function N5(X,Q){return X.directoryLoadInfoById.get(Q)?.state??"loaded"}function o9(X,Q){let Z=i9(X,Q);if(Z.state==="loading"&&Z.activeAttemptId!=null)return{attemptId:Z.activeAttemptId,nodeId:Q,reused:!0};let Y=Z.nextAttemptId;return Z.activeAttemptId=Y,Z.errorMessage=null,Z.nextAttemptId+=1,Z.state="loading",{attemptId:Y,nodeId:Q,reused:!1}}function r9(X,Q){let Z=i9(X,Q);Z.activeAttemptId=null,Z.errorMessage=null,Z.state="unloaded"}function a9(X,Q,Z){let Y=X.directoryLoadInfoById.get(Q);if(Y==null||Y.activeAttemptId!==Z)return!1;return Y.activeAttemptId=null,Y.errorMessage=null,Y.state="loaded",!0}function n9(X,Q,Z){return X.directoryLoadInfoById.get(Q)?.activeAttemptId===Z}function t9(X,Q,Z,Y){let J=X.directoryLoadInfoById.get(Q);if(J==null||J.activeAttemptId!==Z)return!1;return J.activeAttemptId=null,J.errorMessage=Y??null,J.state="error",!0}function e9(X,Q){X.directoryLoadInfoById.delete(Q)}function J0(X,Q,Z){let Y=Z,J=X.listeners.get(Q);if(J!=null)J.add(Y);else X.listeners.set(Q,new Set([Y]));return()=>{let W=X.listeners.get(Q);if(W==null)return;if(W.delete(Y),W.size===0)X.listeners.delete(Q)}}function W0(X){return{affectedAncestorIds:X.affectedAncestorIds??[],affectedNodeIds:X.affectedNodeIds??[],canonicalChanged:!0,operation:"add",path:X.path,projectionChanged:X.projectionChanged,visibleCountDelta:null}}function G0(X){return{affectedAncestorIds:X.affectedAncestorIds??[],affectedNodeIds:X.affectedNodeIds??[],canonicalChanged:!0,operation:"remove",path:X.path,projectionChanged:X.projectionChanged,recursive:X.recursive,visibleCountDelta:null}}function q0(X){return{affectedAncestorIds:X.affectedAncestorIds??[],affectedNodeIds:X.affectedNodeIds??[],canonicalChanged:!0,from:X.from,operation:"move",projectionChanged:X.projectionChanged,to:X.to,visibleCountDelta:null}}function $0(X){return{affectedAncestorIds:X.affectedAncestorIds??[],affectedNodeIds:X.affectedNodeIds??[],canonicalChanged:!1,operation:"expand",path:X.path,projectionChanged:!0,visibleCountDelta:null}}function U0(X){return{affectedAncestorIds:X.affectedAncestorIds??[],affectedNodeIds:X.affectedNodeIds??[],canonicalChanged:!1,operation:"collapse",path:X.path,projectionChanged:!0,visibleCountDelta:null}}function z0(X){return{affectedAncestorIds:X.affectedAncestorIds??[],affectedNodeIds:X.affectedNodeIds??[],canonicalChanged:!1,operation:"mark-directory-unloaded",path:X.path,projectionChanged:X.projectionChanged,visibleCountDelta:null}}function K0(X){return{affectedAncestorIds:X.affectedAncestorIds??[],affectedNodeIds:X.affectedNodeIds??[],attemptId:X.attemptId,canonicalChanged:!1,operation:"begin-child-load",path:X.path,projectionChanged:X.projectionChanged,reused:X.reused,visibleCountDelta:null}}function M0(X){return{affectedAncestorIds:X.affectedAncestorIds??[],affectedNodeIds:X.affectedNodeIds??[],attemptId:X.attemptId,canonicalChanged:X.childEvents.some((Q)=>Q.canonicalChanged),childEvents:X.childEvents,operation:"apply-child-patch",path:X.path,projectionChanged:X.projectionChanged,visibleCountDelta:null}}function H0(X){return{affectedAncestorIds:X.affectedAncestorIds??[],affectedNodeIds:X.affectedNodeIds??[],attemptId:X.attemptId,canonicalChanged:!1,operation:"complete-child-load",path:X.path,projectionChanged:X.projectionChanged,stale:X.stale,visibleCountDelta:null}}function A0(X){return{affectedAncestorIds:X.affectedAncestorIds??[],affectedNodeIds:X.affectedNodeIds??[],attemptId:X.attemptId,canonicalChanged:!1,errorMessage:X.errorMessage,operation:"fail-child-load",path:X.path,projectionChanged:X.projectionChanged,stale:X.stale,visibleCountDelta:null}}function L0(X){return{activeNodeCountAfter:X.activeNodeCountAfter,activeNodeCountBefore:X.activeNodeCountBefore,affectedAncestorIds:X.affectedAncestorIds??[],affectedNodeIds:X.affectedNodeIds??[],cachedPathEntryCountAfter:X.cachedPathEntryCountAfter,cachedPathEntryCountBefore:X.cachedPathEntryCountBefore,canonicalChanged:!1,idsPreserved:X.idsPreserved,loadInfoEntryCountAfter:X.loadInfoEntryCountAfter,loadInfoEntryCountBefore:X.loadInfoEntryCountBefore,mode:X.mode,operation:"cleanup",projectionChanged:X.projectionChanged,reclaimedCachedPathEntryCount:X.reclaimedCachedPathEntryCount,reclaimedLoadInfoEntryCount:X.reclaimedLoadInfoEntryCount,reclaimedNodeSlotCount:X.reclaimedNodeSlotCount,reclaimedSegmentCount:X.reclaimedSegmentCount,segmentCountAfter:X.segmentCountAfter,segmentCountBefore:X.segmentCountBefore,totalNodeSlotCountAfter:X.totalNodeSlotCountAfter,totalNodeSlotCountBefore:X.totalNodeSlotCountBefore,visibleCountDelta:null}}function h4(X,Q,Z){return{...Z,visibleCountDelta:Z8(X)-Q}}function O0(X,Q){let Z=Z8(X),Y=d9();X.transactionStack.push(Y);try{Q()}catch(J){throw Q0(X,Y,!1),J}Q0(X,Y,!0,Z8(X)-Z)}function X5(X,Q){let Z=X.instrumentation;if(Z==null){X0(X,Q);return}S(Z,"store.events.record",()=>X0(X,Q))}function X0(X,Q){let Z=X.transactionStack[X.transactionStack.length-1]??null;if(Z==null){Q8(X,Q);return}Z.events.push(Q),xX(Z,Q)}function Q0(X,Q,Z,Y=null){if(X.transactionStack.pop()!==Q)throw Error("Transaction stack underflow");if(!Z)return;let J=X.transactionStack[X.transactionStack.length-1]??null;if(J!=null){let q=X.instrumentation;if(q==null)Z0(J,Q);else S(q,"store.events.batch.merge",()=>Z0(J,Q));return}let W=fX(Q,Y),G=X.instrumentation;if(G==null){Q8(X,W);return}S(G,"store.events.batch.commit",()=>Q8(X,W))}function fX(X,Q){return{affectedAncestorIds:[...X.affectedAncestorIds],affectedNodeIds:[...X.affectedNodeIds],canonicalChanged:X.events.some((Z)=>Z.canonicalChanged),events:[...X.events],operation:"batch",projectionChanged:X.events.some((Z)=>Z.projectionChanged),visibleCountDelta:Q}}function yX(X,Q){for(let Z of Q.affectedAncestorIds)X.affectedAncestorIds.add(Z);for(let Z of Q.affectedNodeIds)X.affectedNodeIds.add(Z)}function Z0(X,Q){for(let Z of Q.events)X.events.push(Z);yX(X,Q)}function xX(X,Q){for(let Z of Q.affectedNodeIds)X.affectedNodeIds.add(Z);for(let Z of Q.affectedAncestorIds)X.affectedAncestorIds.add(Z)}function Q8(X,Q){let Z=X.instrumentation;if(Z==null){Y0(X,Q);return}S(Z,"store.events.emit",()=>Y0(X,Q))}function Y0(X,Q){X.listeners.get(Q.operation)?.forEach((Z)=>Z(Q)),X.listeners.get("*")?.forEach((Z)=>Z(Q))}function Z8(X){return X.snapshot.nodes[X.snapshot.rootId]?.visibleSubtreeCount??0}function M5(X,Q){if(X.snapshot.options.flattenEmptyDirectories!==!0)return null;let Z=X.snapshot.nodes[Q];if(Z==null||!y(Z)||_4(Z,f4))return null;let Y=X.snapshot.directories.get(Q);if(Y==null||Y.childIds.length!==1)return null;let J=Y.childIds[0];if(J==null)return null;let W=X.snapshot.nodes[J];if(W==null||!y(W))return null;return J}function H5(X,Q){let Z=Q;while(!0){let Y=M5(X,Z);if(Y==null)return Z;Z=Y}}function K6(X,Q){let Z=[Q],Y=Q;while(!0){let J=M5(X,Y);if(J==null)return Z;Z.push(J),Y=J}}function V7(X,Q){let Z=Q==null?X.snapshot.rootId:p4(X,Q);if(Z==null)return[];return IX(X,Z)}function J8(X,Q){let Z=s5(Q),Y=Z.isDirectory?Z.segments:Z.segments.slice(0,-1),J=C5(X,iX(X,Y)),{createdNodeIds:W,directoryId:G}=mX(X,Y),q=new Set(W),U=G;if(Z.isDirectory){let M=I(X,G);if(_4(M,q5))throw Error(`Path already exists: "${Q}"`);U6(M,q5),X.pathCacheByNodeId.set(G,{path:Q,version:X.pathCacheVersion}),q.add(G)}else U=hX(X,G,Z.basename),q.add(U);v5(X,G);let A=C5(X,G);return W0({affectedAncestorIds:n4(X,U),affectedNodeIds:[...q],path:Q,projectionChanged:E0(J,A)})}function W8(X,Q,Z){let Y=p4(X,Q);if(Y==null)throw Error(`Path does not exist: "${Q}"`);let J=I(X,Y);if(_4(J,f4))throw Error("The root node cannot be removed");if(y(J)&&O4(X,Y).childIds.length>0&&Z.recursive!==!0)throw Error(`Cannot remove a non-empty directory without recursive: "${Q}"`);let W=J.parentId,G=C5(X,W),q=R0(X,Y);$8(X,W,Y,J.nameId),U8(X,W),v5(X,W);let U=C5(X,W);return G0({affectedAncestorIds:n4(X,W),affectedNodeIds:q,path:Q,projectionChanged:E0(G,U),recursive:Z.recursive===!0})}function G8(X,Q,Z,Y){let J=p4(X,Q);if(J==null)throw Error(`Source path does not exist: "${Q}"`);let W=I(X,J);if(_4(W,f4))throw Error("The root node cannot be moved");let G=Y.collision??"error",q=dX(X,J,Z),U=C5(X,W.parentId),A=C5(X,q.parentId),M=a4(X.snapshot.segmentTable,W.nameId),O=Y5(X.snapshot.segmentTable,q.basename);if(q.parentId===W.parentId&&M===q.basename)return null;if(y(W)&&rX(X,J,q.parentId))throw Error("Cannot move a directory into one of its descendants");let z=T5(X.snapshot.nodes,O4(X,q.parentId)).get(O),j=q.existingNodeId??z??null;if(j!=null&&j!==J){if(sX(X,j,G,y6(W))==="skip")return null}let B=W.parentId;if($8(X,B,J,W.nameId),W.parentId=q.parentId,W.nameId=O,X.pathCacheByNodeId.delete(J),k0(X,J),q8(X,q.parentId,J),U8(X,B),X.pathCacheVersion++,v5(X,B),q.parentId!==B)v5(X,q.parentId);let R=C5(X,B),D=C5(X,q.parentId);return q0({affectedAncestorIds:[...new Set([...n4(X,B),...n4(X,q.parentId)])],affectedNodeIds:[J],from:Q,projectionChanged:D0([U,A],[R,D]),to:A4(X,J)})}function gX(X,Q){let Z=X.pathCacheByNodeId.get(Q);return Z!=null&&Z.version===X.pathCacheVersion?Z.path:null}function B0(X,Q,Z){return X.pathCacheByNodeId.set(Q,{path:Z,version:X.pathCacheVersion}),Z}function A4(X,Q){let Z=I(X,Q),Y=gX(X,Q);if(Y!=null)return Y;if(_4(Z,f4))return B0(X,Q,"");let J=A4(X,Z.parentId),W=a4(X.snapshot.segmentTable,Z.nameId),G=J.length===0?W:`${J}${W}`;return B0(X,Q,y(Z)?`${G}/`:G)}function v5(X,Q){let Z=X.instrumentation;if(Z==null){_0(X,Q);return}S(Z,"store.recomputeCountsUpwardFrom",()=>_0(X,Q))}function m6(X,Q){let Z=[[Q,0]],{nodes:Y,directories:J}=X.snapshot;while(Z.length>0){let W=Z[Z.length-1],G=W[0],q=Y[G];if(q==null||!y(q)){Y8(X,G,q,!0),Z.pop();continue}let U=J.get(G);if(U==null||W[1]>=U.childIds.length){Y8(X,G,q,!0),Z.pop();continue}let A=U.childIds[W[1]++];Z.push([A,0])}}function n4(X,Q){let Z=[],Y=Q;while(Y!=null){let J=I(X,Y);if(Z.push(Y),Y===X.snapshot.rootId)break;Y=J.parentId}return Z}function p4(X,Q){if(Q.length===0)return X.snapshot.rootId;let Z=B7(Q);return V0(X,Z.segments,Z.requiresDirectory)}function V0(X,Q,Z){let Y=X.snapshot.rootId;for(let W of Q){let G=X.snapshot.segmentTable.idByValue.get(W);if(G===void 0)return null;let q=O4(X,Y),U=T5(X.snapshot.nodes,q).get(G);if(U===void 0)return null;Y=U}let J=I(X,Y);if(Z&&!y(J))return null;return Y}function O4(X,Q){let Z=X.snapshot.directories.get(Q);if(Z===void 0)throw Error(`Unknown directory child index for node ${String(Q)}`);return Z}function I(X,Q){let Z=X.snapshot.nodes[Q];if(Z===void 0||_4(Z,l5))throw Error(`Unknown node ID: ${String(Q)}`);return Z}function IX(X,Q){let Z=X.snapshot.nodes[Q];if(Z===void 0||_4(Z,l5))return[];if(!y(Z))return[A4(X,Q)];if(O4(X,Q).childIds.length===0)return _4(Z,q5)&&!_4(Z,f4)?[A4(X,Q)]:[];let Y=[],J=[{childIndex:0,nodeId:Q}];while(J.length>0){let W=J[J.length-1];if(W==null)break;let G=X.snapshot.nodes[W.nodeId];if(G===void 0||_4(G,l5)){J.pop();continue}if(!y(G)){Y.push(A4(X,W.nodeId)),J.pop();continue}let q=O4(X,W.nodeId);if(q.childIds.length===0){if(_4(G,q5)&&!_4(G,f4))Y.push(A4(X,W.nodeId));J.pop();continue}let U=q.childIds[W.childIndex];if(U==null){J.pop();continue}W.childIndex++,J.push({childIndex:0,nodeId:U})}return Y}function mX(X,Q){let Z=[],Y=X.snapshot.rootId;for(let J of Q){let W=Y5(X.snapshot.segmentTable,J),G=O4(X,Y),q=T5(X.snapshot.nodes,G).get(W);if(q!==void 0){if(!y(I(X,q)))throw Error(`Cannot create a directory that collides with an existing file: "${J}"`);Y=q;continue}Y=uX(X,Y,W),Z.push(Y)}return{createdNodeIds:Z,directoryId:Y}}function uX(X,Q,Z){let Y=I(X,Q),J=X.snapshot.nodes.length;if(X.snapshot.nodes.push({depthAndFlags:u4(s4(Y)+1,0,d4),nameId:Z,parentId:Q,subtreeNodeCount:1,visibleSubtreeCount:1}),X.snapshot.directories.set(J,h5()),q8(X,Q,J),X.collapseNewDirectoriesByDefault)X.collapsedDirectoryIds.add(J),X.hasCollapsedDirectoryOverrides=!0;return X.activeNodeCount++,J}function hX(X,Q,Z){let Y=Y5(X.snapshot.segmentTable,Z),J=O4(X,Q);if(T5(X.snapshot.nodes,J).has(Y))throw Error(`Path already exists: "${aX(X,Q,Z)}"`);let W=I(X,Q),G=X.snapshot.nodes.length;return X.snapshot.nodes.push({depthAndFlags:u4(s4(W)+1,0),nameId:Y,parentId:Q,subtreeNodeCount:1,visibleSubtreeCount:1}),q8(X,Q,G),X.activeNodeCount++,G}function pX(X,Q,Z){let Y=0,J=Q.childIds.length;while(Y<J){let W=Y+J>>>1,G=Q.childIds[W];if(G==null){J=W;continue}if(cX(X,Z,G)<0)J=W;else Y=W+1}return Y}function q8(X,Q,Z){let Y=O4(X,Q),J=I(X,Z);T5(X.snapshot.nodes,Y).set(J.nameId,Z),A7(Y,Z,J.subtreeNodeCount,J.visibleSubtreeCount);let W=pX(X,Y,Z);Y.childIds.splice(W,0,Z),n7(Y,W),c5(X.snapshot.nodes,Y)}function $8(X,Q,Z,Y){let J=O4(X,Q),W=q6(J),G=W.get(Z)??-1;T5(X.snapshot.nodes,J).delete(Y),W.delete(Z);let q=X.snapshot.nodes[Z];if(q!=null)A7(J,Z,-q.subtreeNodeCount,-q.visibleSubtreeCount);if(G>=0)J.childIds.splice(G,1),n7(J,G),c5(X.snapshot.nodes,J)}function cX(X,Q,Z){let Y=X.snapshot.options.sort;if(Y==="default")return lX(X,Q,Z);return Y(j0(X,Q),j0(X,Z))}function lX(X,Q,Z){let Y=I(X,Q),J=I(X,Z),W=y(Y);if(W!==y(J))return W?-1:1;let G=g6(I6(X.snapshot.segmentTable,Y.nameId),I6(X.snapshot.segmentTable,J.nameId));if(G!==0)return G;let q=a4(X.snapshot.segmentTable,Y.nameId),U=a4(X.snapshot.segmentTable,J.nameId);if(q!==U)return q<U?-1:1;return Q<Z?-1:1}function j0(X,Q){let Z=I(X,Q),Y=A4(X,Q),J=y(Z),W=J?Y.slice(0,-1):Y;return{basename:a4(X.snapshot.segmentTable,Z.nameId),depth:s4(Z),isDirectory:J,path:Y,segments:W.length===0?[]:W.split("/")}}function dX(X,Q,Z){let Y=I(X,Q),J=p4(X,Z);if(J!=null){let A=I(X,J);if(y(A))return{basename:a4(X.snapshot.segmentTable,Y.nameId),existingNodeId:null,parentId:J};let M=B7(Z).segments;return{basename:M[M.length-1]??"",existingNodeId:J,parentId:A.parentId}}let W=B7(Z),G=W.segments[W.segments.length-1]??"",q=W.segments.slice(0,-1),U=q.length===0?X.snapshot.rootId:V0(X,q,!0);if(U==null)throw Error(`Destination parent does not exist: "${Z}"`);return{basename:G,existingNodeId:null,parentId:U}}function sX(X,Q,Z,Y){if(Z==="skip")return"skip";if(Z==="error")throw Error(`Destination already exists: "${A4(X,Q)}"`);let J=I(X,Q);if(y6(J)!==Y)throw Error("replace collision requires the same source and destination kinds");if(y(J)&&O4(X,Q).childIds.length>0)throw Error("replace collision does not support non-empty directories");let{parentId:W,nameId:G}=J;return R0(X,Q),$8(X,W,Q,G),U8(X,W),v5(X,W),"handled"}function R0(X,Q){let Z=[],Y=[{nodeId:Q,visitedChildren:!1}];while(Y.length>0){let J=Y.pop();if(J==null)break;let W=I(X,J.nodeId);if(J.visitedChildren||!y(W)){if(y(W))X.snapshot.directories.delete(J.nodeId);if(U6(W,l5),X.pathCacheByNodeId.delete(J.nodeId),X.collapsedDirectoryIds.delete(J.nodeId))X.hasCollapsedDirectoryOverrides=X.collapsedDirectoryIds.size>0;X.expandedDirectoryIds.delete(J.nodeId),e9(X,J.nodeId),X.activeNodeCount--,Z.push(J.nodeId);continue}Y.push({nodeId:J.nodeId,visitedChildren:!0});let G=O4(X,J.nodeId);for(let q=G.childIds.length-1;q>=0;q--){let U=G.childIds[q];if(U!=null)Y.push({nodeId:U,visitedChildren:!1})}}return Z}function U8(X,Q){let Z=Q;while(Z!=null){let Y=I(X,Z);if(!y(Y)||_4(Y,f4))return;if(O4(X,Z).childIds.length>0)return;U6(Y,q5),Z=Y.parentId===Z?null:Y.parentId}}function iX(X,Q){let Z=X.snapshot.rootId;for(let Y of Q){let J=X.snapshot.segmentTable.idByValue.get(Y);if(J==null)break;let W=T5(X.snapshot.nodes,O4(X,Z)).get(J);if(W==null)break;if(!y(I(X,W)))break;Z=W}return Z}function C5(X,Q){let Z=oX(X,Q);if(Z==null)return null;let Y=H5(X,Z),J=I(X,Y),W=Z===Y?null:K6(X,Z).map((G)=>A4(X,G));return JSON.stringify({flattenedSegmentPaths:W,hasChildren:O4(X,Y).childIds.length>0,path:A4(X,Y),terminalKind:y6(J)})}function E0(X,Q){return D0([X],[Q])}function D0(X,Q){for(let Z=0;Z<X.length;Z+=1){let Y=X[Z],J=Q[Z];if(Y==null||J==null||Y!==J)return!0}return!1}function oX(X,Q){let Z=Q;while(Z!=null){let Y=I(X,Z);if(!y(Y)||_4(Y,f4))return null;if(!y4(X,Z,Y))return Z;Z=Y.parentId}return null}function k0(X,Q){let Z=I(X,Q);if(T9(Z,(Q===X.snapshot.rootId?-1:s4(I(X,Z.parentId)))+1),!y(Z))return;let Y=O4(X,Q);for(let J of Y.childIds)k0(X,J)}function rX(X,Q,Z){let Y=Z;while(Y!=null){if(Y===Q)return!0;let J=I(X,Y);if(Y===X.snapshot.rootId)return!1;Y=J.parentId}return!1}function Y8(X,Q,Z=I(X,Q),Y=!1){let J=X.instrumentation;if(J==null){F0(X,Q,Z,Y);return}S(J,"store.recomputeNodeCounts",()=>F0(X,Q,Z,Y))}function _0(X,Q){let Z=Q;while(Z!=null){let Y=I(X,Z),J=Y.subtreeNodeCount,W=Y.visibleSubtreeCount;if(Y8(X,Z,Y),Z===X.snapshot.rootId)return;let G=Y.subtreeNodeCount-J,q=Y.visibleSubtreeCount-W,U=Y.parentId;if(G!==0||q!==0)A7(O4(X,U),Z,G,q);Z=U}}function F0(X,Q,Z,Y){if(!y(Z)){Z.subtreeNodeCount=1,Z.visibleSubtreeCount=1;return}let J=O4(X,Q);if(Y){let q=X.instrumentation;if(q==null)p5(X.snapshot.nodes,J);else S(q,"store.recomputeNodeCounts.rebuildChildAggregates",()=>p5(X.snapshot.nodes,J))}let W=1+J.totalChildSubtreeNodeCount,G=J.totalChildVisibleSubtreeCount;if(Z.subtreeNodeCount=W,_4(Z,f4)){Z.visibleSubtreeCount=G;return}Z.visibleSubtreeCount=M5(X,Q)!=null?G:y4(X,Q,Z)?1+G:1}function aX(X,Q,Z){let Y=A4(X,Q);return Y.length===0?Z:`${Y}${Z}`}function M6(X){return X!=null&&!_4(X,l5)}function R7(X,Q){let Z=X.snapshot.nodes[Q];if(!M6(Z)||!y(Z)||_4(Z,f4))return null;return Z}function nX(X){let Q=0;for(let[Z,Y]of X.pathCacheByNodeId){if(Y.version!==X.pathCacheVersion)continue;if(!M6(X.snapshot.nodes[Z]))continue;Q+=1}return Q}function tX(X){return Math.max(0,X.valueById.length-1)}function T0(X){return{activeNodeCount:X.activeNodeCount,cachedPathEntryCount:nX(X),loadInfoEntryCount:X.directoryLoadInfoById.size,segmentCount:tX(X.snapshot.segmentTable),totalNodeSlotCount:Math.max(0,X.snapshot.nodes.length-1)}}function eX(X,Q,Z,Y){return{activeNodeCountAfter:Y.activeNodeCount,activeNodeCountBefore:Z.activeNodeCount,cachedPathEntryCountAfter:Y.cachedPathEntryCount,cachedPathEntryCountBefore:Z.cachedPathEntryCount,idsPreserved:Q,loadInfoEntryCountAfter:Y.loadInfoEntryCount,loadInfoEntryCountBefore:Z.loadInfoEntryCount,mode:X,reclaimedCachedPathEntryCount:Z.cachedPathEntryCount-Y.cachedPathEntryCount,reclaimedLoadInfoEntryCount:Z.loadInfoEntryCount-Y.loadInfoEntryCount,reclaimedNodeSlotCount:Z.totalNodeSlotCount-Y.totalNodeSlotCount,reclaimedSegmentCount:Z.segmentCount-Y.segmentCount,segmentCountAfter:Y.segmentCount,segmentCountBefore:Z.segmentCount,totalNodeSlotCountAfter:Y.totalNodeSlotCount,totalNodeSlotCountBefore:Z.totalNodeSlotCount}}function w0(X){let Q=[],Z=[];for(let Y of X.collapsedDirectoryIds)if(R7(X,Y)!=null)Q.push(A4(X,Y));for(let Y of X.expandedDirectoryIds)if(R7(X,Y)!=null)Z.push(A4(X,Y));return{collapsedPaths:Q,expandedPaths:Z}}function N0(X){let Q=[];for(let[Z,Y]of X.directoryLoadInfoById){if(R7(X,Z)==null||N5(X,Z)==="loaded")continue;Q.push({info:{activeAttemptId:null,errorMessage:Y.errorMessage,nextAttemptId:Y.nextAttemptId,state:Y.state},path:A4(X,Z)})}return Q}function C0(X,Q){X.collapsedDirectoryIds.clear(),X.hasCollapsedDirectoryOverrides=!1,X.expandedDirectoryIds.clear();for(let Z of Q.expandedPaths){let Y=p4(X,Z);if(Y==null)continue;w5(X,Y,!0,I(X,Y))}for(let Z of Q.collapsedPaths){let Y=p4(X,Z);if(Y==null)continue;w5(X,Y,!1,I(X,Y))}}function v0(X,Q){X.directoryLoadInfoById.clear();for(let Z of Q){let Y=p4(X,Z.path);if(Y==null)continue;if(R7(X,Y)==null)continue;X.directoryLoadInfoById.set(Y,{activeAttemptId:null,errorMessage:Z.info.errorMessage,nextAttemptId:Z.info.nextAttemptId,state:Z.info.state})}}function XQ(X){X.pathCacheVersion+=1,X.pathCacheByNodeId.clear(),X.pathCacheByNodeId.set(X.snapshot.rootId,{path:"",version:X.pathCacheVersion})}function QQ(X){let Q=X.snapshot.segmentTable,Z=j7();for(let Y of X.snapshot.nodes){if(!M6(Y))continue;if(_4(Y,f4)){Y.nameId=0;continue}Y.nameId=Y5(Z,a4(Q,Y.nameId))}X.snapshot.segmentTable=Z}function ZQ(X){for(let[Q,Z]of X.snapshot.directories){let Y=X.snapshot.nodes[Q];if(!M6(Y)||!y(Y)){X.snapshot.directories.delete(Q);continue}let J=Z.childIds.filter((W)=>{let G=X.snapshot.nodes[W];return M6(G)&&G.parentId===Q});Z.childIds=J,Z.childIdByNameId=new Map(J.map((W)=>[I(X,W).nameId,W])),Z.childPositionById=new Map(J.map((W,G)=>[W,G])),p5(X.snapshot.nodes,Z)}}function YQ(X){let Q=X.snapshot.nodes.length-1;while(Q>X.snapshot.rootId){let Z=X.snapshot.nodes[Q];if(M6(Z))break;Q-=1}X.snapshot.nodes.length=Q+1}function JQ(X){let Q=w0(X),Z=N0(X);S(X.instrumentation,"store.cleanup.stable.clearPathCaches",()=>XQ(X)),S(X.instrumentation,"store.cleanup.stable.rebuildSegmentTable",()=>QQ(X)),S(X.instrumentation,"store.cleanup.stable.rebuildDirectoryIndexes",()=>ZQ(X)),S(X.instrumentation,"store.cleanup.stable.trimTrailingRemovedNodeSlots",()=>YQ(X)),S(X.instrumentation,"store.cleanup.stable.restoreExpansionOverrides",()=>C0(X,Q)),S(X.instrumentation,"store.cleanup.stable.restoreDirectoryLoadInfos",()=>v0(X,Z)),S(X.instrumentation,"store.cleanup.stable.recomputeCounts",()=>m6(X,X.snapshot.rootId))}function WQ(X){let Q=w0(X),Z=N0(X),Y=S(X.instrumentation,"store.cleanup.aggressive.listPaths",()=>V7(X)),J=N9({...X.snapshot.options},X.instrumentation),W=S(X.instrumentation,"store.cleanup.aggressive.rebuildSnapshot",()=>{let G=new F7(J);return G.appendPaths(Y),G.finish()});X.snapshot=W,X.activeNodeCount=W.nodes.length-1,X.pathCacheByNodeId=new Map([[W.rootId,{path:"",version:0}]]),X.pathCacheVersion=0,S(X.instrumentation,"store.cleanup.aggressive.restoreExpansionOverrides",()=>C0(X,Q)),S(X.instrumentation,"store.cleanup.aggressive.restoreDirectoryLoadInfos",()=>v0(X,Z)),S(X.instrumentation,"store.cleanup.aggressive.recomputeCounts",()=>m6(X,X.snapshot.rootId))}function b0(X){for(let Q of X.directoryLoadInfoById.values())if(Q.state==="loading"&&Q.activeAttemptId!=null)return!0;return!1}function S0(X,Q){let Z=T0(X);if(Q==="stable")S(X.instrumentation,"store.cleanup.stable",()=>JQ(X));else S(X.instrumentation,"store.cleanup.aggressive",()=>WQ(X));let Y=T0(X);return eX(Q,Q==="stable",Z,Y)}var GQ=64;function qQ(X,Q){let Z=Q+2;if(Z<=X.length)return X;let Y=X.length;while(Y<Z)Y*=2;let J=new Int32Array(Y);return J.fill(-1),J.set(X),J}function x4(X){return I(X,X.snapshot.rootId).visibleSubtreeCount}function x0(X,Q,Z,Y){let J=I(X,Q.terminalNodeId),W=Math.max(1,J.visibleSubtreeCount);return Math.min(Y-1,Z+W-1)}function $Q(X,Q,Z,Y){return{ancestorPaths:Y,index:Q.index,posInSet:Q.posInSet,row:u6(X,Q.cursor),setSize:Q.setSize,subtreeEndIndex:x0(X,Q.cursor,Q.index,Z)}}function g0(X,Q,Z,Y,J,W){let G=O4(X,Q),{childIndex:q,childVisibleIndex:U,localVisibleIndex:A}=L7(X.snapshot.nodes,G,Z),M=G.childIds[q];if(M==null)throw Error(`Visible index ${String(Z)} is out of range`);return UQ(X,M,A,Y+U,J+1,q,G.childIds.length,W)}function UQ(X,Q,Z,Y,J,W,G,q){if(!y(I(X,Q))){if(Z===0)return{ancestors:q,cursor:{headNodeId:Q,terminalNodeId:Q,visibleDepth:J},index:Y,posInSet:W,setSize:G};throw Error(`Visible index ${String(Z)} is out of range for file`)}let U=d0(X,Q,J);if(Z===0)return{ancestors:q,cursor:U,index:Y,posInSet:W,setSize:G};let A=I(X,U.terminalNodeId);if(!y(A)||!y4(X,U.terminalNodeId,A))throw Error(`Visible index ${String(Z)} is out of range for collapsed directory`);return g0(X,U.terminalNodeId,Z-1,Y+1,U.visibleDepth,[...q,{cursor:U,index:Y,posInSet:W,setSize:G}])}function I0(X,Q){let Z=x4(X);if(Q<0||Q>=Z)return null;let Y=g0(X,X.snapshot.rootId,Q,0,-1,[]),J=Y.ancestors.map((G)=>A4(X,G.cursor.terminalNodeId)),W=null;return{ancestorPaths:J,get ancestorRows(){if(W!=null)return W;let G=[],q=[];for(let U of Y.ancestors){let A=$Q(X,U,Z,[...q]);G.push(A),q.push(A.row.path)}return W=G,W},index:Y.index,posInSet:Y.posInSet,row:u6(X,Y.cursor),setSize:Y.setSize,subtreeEndIndex:x0(X,Y.cursor,Y.index,Z)}}function m0(X,Q,Z){let Y=X.instrumentation,J=x4(X);if(J<=0||Z<Q)return[];let W=Math.max(0,Math.min(Q,J-1)),G=Math.max(W,Math.min(Z,J-1));if(Y==null){if(W===0)return MQ(X,G+1);let O=[],z=P0(X,W);for(let j=W;j<=G&&z!=null;j++){let B=u6(X,z);O.push(B),z=f0(X,z)}return O}let q=[],U=0,A=0,M=S(Y,"store.getVisibleSlice.selectFirstRow",()=>P0(X,W));for(let O=W;O<=G&&M!=null;O++){let z=S(Y,"store.getVisibleSlice.materializeRow",()=>u6(X,M));if(q.push(z),z.isFlattened)U++,A+=z.flattenedSegments?.length??0;M=S(Y,"store.getVisibleSlice.advanceCursor",()=>f0(X,M))}return z6(Y,"workload.visibleRowsRead",q.length),z6(Y,"workload.flattenedRowsRead",U),z6(Y,"workload.flattenedSegmentsRead",A),q}function K8(X,Q=x4(X)){let Z=X.instrumentation;if(Z==null)return y0(X,Q);return S(Z,"store.getVisibleTreeProjection",()=>y0(X,Q))}function u0(X){return KQ(K8(X))}function h0(X,Q){let Z=p4(X,Q);if(Z==null||Z===X.snapshot.rootId)return null;if(y(I(X,Z))&&H5(X,Z)!==Z)return null;let Y=0,J=Z,{nodes:W,rootId:G}=X.snapshot;while(J!==G){let q=I(X,J).parentId,U=O4(X,q),A=q6(U).get(J);if(A==null)throw Error(`Child ${String(J)} was not found in its parent index`);if(Y+=E9(W,U,A),q!==G){let M=I(X,q),O=M5(X,q);if(!y4(X,q,M)&&O!==J)return null;if(H5(X,q)===q)Y+=1}J=q}return Y}function p0(X,Q){let Z=p4(X,Q);if(Z==null)throw Error(`Path does not exist: "${Q}"`);let Y=I(X,Z);if(!y(Y))throw Error(`Path is not a directory: "${Q}"`);if(y4(X,Z,Y))return null;return w5(X,Z,!0,Y),v5(X,Z),$0({affectedAncestorIds:n4(X,Z),affectedNodeIds:[Z],path:Q,projectionChanged:!0})}function c0(X,Q){let Z=p4(X,Q);if(Z==null)throw Error(`Path does not exist: "${Q}"`);let Y=I(X,Z);if(!y(Y))throw Error(`Path is not a directory: "${Q}"`);if(!y4(X,Z,Y))return null;return w5(X,Z,!1,Y),v5(X,Z),U0({affectedAncestorIds:n4(X,Z),affectedNodeIds:[Z],path:Q,projectionChanged:!0})}function P0(X,Q){if(Q<0||Q>=x4(X))return null;return l0(X,X.snapshot.rootId,Q,-1)}function l0(X,Q,Z,Y){let J=O4(X,Q),W=X.instrumentation,{childIndex:G,localVisibleIndex:q}=W==null?L7(X.snapshot.nodes,J,Z):S(W,"store.getVisibleSlice.selectChildIndex",()=>L7(X.snapshot.nodes,J,Z)),U=J.childIds[G];if(U!=null)return z8(X,U,q,Y+1);throw Error(`Visible index ${String(Z)} is out of range`)}function z8(X,Q,Z,Y){if(!y(I(X,Q))){if(Z===0)return{headNodeId:Q,terminalNodeId:Q,visibleDepth:Y};throw Error(`Visible index ${String(Z)} is out of range for file`)}let J=d0(X,Q,Y);if(Z===0)return J;let W=I(X,J.terminalNodeId);if(!y(W)||!y4(X,J.terminalNodeId,W))throw Error(`Visible index ${String(Z)} is out of range for collapsed directory`);return l0(X,J.terminalNodeId,Z-1,J.visibleDepth)}function d0(X,Q,Z){if(!y(I(X,Q)))return{headNodeId:Q,terminalNodeId:Q,visibleDepth:Z};if(X.instrumentation==null)return{headNodeId:Q,terminalNodeId:H5(X,Q),visibleDepth:Z};return{headNodeId:Q,terminalNodeId:S(X.instrumentation,"store.getVisibleSlice.flatten.resolveTerminalDirectory",()=>H5(X,Q)),visibleDepth:Z}}function zQ(X,Q){let Z=I(X,Q);if(!y(Z))return!0;let Y=Z.parentId;if(Y===X.snapshot.rootId)return!0;return M5(X,Y)!==Q}function f0(X,Q){let Z=I(X,Q.terminalNodeId);if(y(Z)){let W=O4(X,Q.terminalNodeId);if(y4(X,Q.terminalNodeId,Z)&&W.childIds.length>0){let G=W.childIds[0];return G==null?null:z8(X,G,0,Q.visibleDepth+1)}}let{terminalNodeId:Y,visibleDepth:J}=Q;while(!0){let W=I(X,Y);if(Y===X.snapshot.rootId)return null;let G=W.parentId,q=O4(X,G),U=q6(q).get(Y)??-1;if(U<0)throw Error(`Child ${String(Y)} was not found in its parent index`);let A=q.childIds[U+1]??null;if(A!=null)return z8(X,A,0,J);if(zQ(X,Y))J--;Y=G}}function KQ(X){let Q=X.paths.length,Z=Array(Q);for(let Y=0;Y<Q;Y+=1){let J=X.getParentIndex(Y);Z[Y]={index:Y,parentPath:J>=0?X.paths[J]??null:null,path:X.paths[Y]??"",posInSet:X.posInSetByIndex[Y]??0,setSize:X.setSizeByIndex[Y]??0}}return{getParentIndex:X.getParentIndex,rows:Z,get visibleIndexByPath(){return X.visibleIndexByPath}}}function y0(X,Q){let Z=Array(Q),Y=new Int32Array(Q),J=new Int32Array(Q),W=new Int32Array(Q),G=new Int32Array(GQ);G.fill(-1);let q=0,{nodes:U,directories:A,segmentTable:M}=X.snapshot,O=[[A.get(X.snapshot.rootId),0,-1,""]],z=X.snapshot.options.flattenEmptyDirectories,j=X.pathCacheByNodeId,B=X.pathCacheVersion,R=M.valueById;while(O.length>0&&q<Q){let V=O[O.length-1],k=V[0];if(V[1]>=k.childIds.length){O.pop();continue}let P=V[1],h=k.childIds[V[1]++],G4=U[h],z4=V[2]+1,d=V[3];G=qQ(G,z4);let Y4,q4=h;if(!y(G4)){let e=j.get(h);Y4=e!=null&&e.version===B?e.path:`${d}${R[G4.nameId]}`}else q4=z?H5(X,h):h,Y4=q4===h?`${d}${R[G4.nameId]}/`:A4(X,q4);Y[q]=G[z4],Z[q]=Y4,J[q]=P,W[q]=k.childIds.length,G[z4+1]=q,q+=1;let t=U[q4];if(t!=null&&y(t)&&y4(X,q4,t))O.push([A.get(q4),0,z4,Y4])}if(q<Q)Z.length=q;let D=Y.subarray(0,q),b=J.subarray(0,q),w=W.subarray(0,q),F=null;return{getParentIndex(V){return V<0||V>=q?-1:D[V]??-1},paths:Z,posInSetByIndex:b,setSizeByIndex:w,get visibleIndexByPath(){if(F==null){F=new Map;for(let V=0;V<q;V+=1)F.set(Z[V]??"",V)}return F}}}function MQ(X,Q){let Z=Array(Q),Y=0,{nodes:J,directories:W,segmentTable:G}=X.snapshot,q=[[W.get(X.snapshot.rootId),0,-1]],U=G.valueById,A=X.snapshot.options.flattenEmptyDirectories,M=X.pathCacheByNodeId,O=X.pathCacheVersion;while(q.length>0&&Y<Q){let z=q[q.length-1],j=z[0];if(z[1]>=j.childIds.length){q.pop();continue}let B=j.childIds[z[1]++],R=J[B],D=z[2]+1;if(!y(R)){let V=M.get(B);Z[Y++]={depth:D,flattenedSegments:void 0,hasChildren:!1,id:B,isExpanded:!1,isFlattened:!1,isLoading:!1,kind:"file",loadState:void 0,name:U[R.nameId],path:V!=null&&V.version===O?V.path:A4(X,B)};continue}let b=A?H5(X,B):B,w={headNodeId:B,terminalNodeId:b,visibleDepth:D};Z[Y++]=u6(X,w);let F=J[b];if(F!=null&&y(F)&&y4(X,b,F))q.push([W.get(b),0,D])}if(Y<Q)Z.length=Y;return Z}function u6(X,Q){let Z=I(X,Q.terminalNodeId),Y=y(Z)?HQ(X,Q):null,J=A4(X,Q.terminalNodeId),W=a4(X.snapshot.segmentTable,Z.nameId),G=y(Z)&&O4(X,Q.terminalNodeId).childIds.length>0,q=Q.headNodeId!==Q.terminalNodeId,U=X.instrumentation,A=q?U==null?K6(X,Q.headNodeId).map((M)=>{let O=I(X,M);return{isTerminal:M===Q.terminalNodeId,name:a4(X.snapshot.segmentTable,O.nameId),nodeId:M,path:A4(X,M)}}):S(U,"store.getVisibleSlice.flatten.collectSegments",()=>K6(X,Q.headNodeId).map((M)=>{let O=I(X,M);return{isTerminal:M===Q.terminalNodeId,name:a4(X.snapshot.segmentTable,O.nameId),nodeId:M,path:A4(X,M)}})):void 0;return{depth:Q.visibleDepth,flattenedSegments:A,hasChildren:G,id:Q.terminalNodeId,isExpanded:y(Z)&&y4(X,Q.terminalNodeId,Z),isFlattened:q,isLoading:Y==="loading",kind:y(Z)?"directory":"file",loadState:Y==null||Y==="loaded"?void 0:Y,name:W,path:J}}function HQ(X,Q){if(Q.headNodeId===Q.terminalNodeId)return N5(X,Q.terminalNodeId);let Z=K6(X,Q.headNodeId),Y=!1,J=!1;for(let W of Z){let G=N5(X,W);if(G==="loading")return"loading";if(G==="error"){J=!0;continue}if(G==="unloaded")Y=!0}if(J)return"error";if(Y)return"unloaded";return"loaded"}function AQ(X){let{directories:Q,nodes:Z,options:Y,rootId:J,presortedDirectoryNodeIds:W}=X.snapshot,G=Y.flattenEmptyDirectories===!0,q=(j)=>{let B=Z[j];if(B==null||!y(B))return;let R=Q.get(j);if(R==null)throw Error(`Unknown directory child index for node ${String(j)}`);let D=R.childIds,b=D.length,w=0,F=0;for(let k=0;k<b;k++){let P=D[k];if(P==null)continue;let h=Z[P];w+=h.subtreeNodeCount,F+=h.visibleSubtreeCount}if(R.totalChildSubtreeNodeCount=w,R.totalChildVisibleSubtreeCount=F,b>=R9)c5(Z,R);B.subtreeNodeCount=1+w;let V;if(G&&b===1){let k=Z[D[0]];V=k!=null&&y(k)?F:1+F}else V=1+F;B.visibleSubtreeCount=V};if(W!=null)for(let j=W.length-1;j>=0;j--)q(W[j]);else for(let j=Z.length-1;j>=1;j--)q(j);let U=Z[J],A=Q.get(J);if(U==null||A==null)return;let M=A.childIds,O=0,z=0;for(let j=0;j<M.length;j++){let B=M[j];if(B==null)continue;let R=Z[B];O+=R.subtreeNodeCount,z+=R.visibleSubtreeCount}A.totalChildSubtreeNodeCount=O,A.totalChildVisibleSubtreeCount=z,c5(Z,A),U.subtreeNodeCount=1+O,U.visibleSubtreeCount=z}function LQ(X){return X.initialExpansion==="open"&&(X.initialExpandedPaths==null||X.initialExpandedPaths.length===0)}var M8=class X{#X;constructor(Q={}){let Z=x6(Q),Y=S(Z,"store.builder.create",()=>new F7(Q));if(Q.preparedInput!=null){let q=p9(Q.preparedInput);if(q!=null)Y.appendPresortedPaths(q,c9(Q.preparedInput));else Y.appendPreparedPaths(h9(Q.preparedInput),!1)}else{let q=Q.paths??[];if(Q.presorted===!0)Y.appendPaths(q);else Y.appendPreparedPaths(S(Z,"store.preparePathEntries",()=>_7(q,Q)))}let J=S(Z,"store.builder.finish",()=>Y.finish({skipSubtreeCountPass:!0})),W=S(Z,"store.state.detectAllDirectoriesExpanded",()=>(Q.initialExpansion??"closed")==="closed"&&Y.didMatchAllInitialExpandedPaths());if(this.#X=S(Z,"store.state.create",()=>l9(J,W?"open":Q.initialExpansion??"closed",Z)),W)this.#X.collapseNewDirectoriesByDefault=!0;let G=W?this.#X.snapshot.directories.size-1:S(Z,"store.state.initializeExpandedPaths",()=>this.initializeExpandedPaths(Q.initialExpandedPaths));if(W||LQ(Q)||(Q.initialExpansion??"closed")==="closed"&&G===this.#X.snapshot.directories.size-1||(Q.initialExpandedPaths?.length??0)>0&&S(Z,"store.state.checkAllDirectoriesExpanded",()=>this.hasAllDirectoriesExpanded()))S(Z,"store.state.initializeOpenVisibleCounts",()=>AQ(this.#X));else S(Z,"store.state.recomputeCounts",()=>m6(this.#X,this.#X.snapshot.rootId))}static preparePaths(Q,Z={}){return I9(Q,Z)}static prepareInput(Q,Z={}){return m9(Q,Z)}static preparePresortedInput(Q){return u9(Q)}list(Q){return S(this.#X.instrumentation,"store.list",()=>V7(this.#X,Q))}add(Q){S(this.#X.instrumentation,"store.add",()=>{let Z=x4(this.#X);X5(this.#X,h4(this.#X,Z,J8(this.#X,Q)))})}remove(Q,Z={}){S(this.#X.instrumentation,"store.remove",()=>{let Y=x4(this.#X);X5(this.#X,h4(this.#X,Y,W8(this.#X,Q,Z)))})}move(Q,Z,Y={}){S(this.#X.instrumentation,"store.move",()=>{let J=x4(this.#X),W=G8(this.#X,Q,Z,Y);if(W!=null)X5(this.#X,h4(this.#X,J,W))})}batch(Q){O0(this.#X,()=>{if(typeof Q==="function"){Q(this);return}for(let Z of Q)switch(Z.type){case"add":this.add(Z.path);break;case"remove":this.remove(Z.path,{recursive:Z.recursive});break;case"move":this.move(Z.from,Z.to,{collision:Z.collision});break}})}getVisibleCount(){return S(this.#X.instrumentation,"store.getVisibleCount",()=>x4(this.#X))}getVisibleSlice(Q,Z){return S(this.#X.instrumentation,"store.getVisibleSlice",()=>m0(this.#X,Q,Z))}getVisibleRowContext(Q){return S(this.#X.instrumentation,"store.getVisibleRowContext",()=>I0(this.#X,Q))}getVisibleTreeProjection(){return u0(this.#X)}getVisibleTreeProjectionData(Q){return K8(this.#X,Q)}getVisibleIndex(Q){return S(this.#X.instrumentation,"store.getVisibleIndex",()=>h0(this.#X,Q))}getPathInfo(Q){return S(this.#X.instrumentation,"store.getPathInfo",()=>{let Z=p4(this.#X,Q);if(Z==null)return null;let Y=I(this.#X,Z);return{depth:s4(Y),kind:y(Y)?"directory":"file",path:A4(this.#X,Z)}})}isExpanded(Q){return S(this.#X.instrumentation,"store.isExpanded",()=>{let Z=this.requireDirectoryNodeId(Q),Y=I(this.#X,Z);return y4(this.#X,Z,Y)})}expand(Q){S(this.#X.instrumentation,"store.expand",()=>{let Z=x4(this.#X),Y=p0(this.#X,Q);if(Y!=null)X5(this.#X,h4(this.#X,Z,Y))})}collapse(Q){S(this.#X.instrumentation,"store.collapse",()=>{let Z=x4(this.#X),Y=c0(this.#X,Q);if(Y!=null)X5(this.#X,h4(this.#X,Z,Y))})}on(Q,Z){return J0(this.#X,Q,Z)}getDirectoryLoadState(Q){let Z=this.requireDirectoryNodeId(Q);return N5(this.#X,Z)}markDirectoryUnloaded(Q){S(this.#X.instrumentation,"store.markDirectoryUnloaded",()=>{let Z=this.requireDirectoryNodeId(Q);if(O4(this.#X,Z).childIds.length>0)throw Error(`Cannot mark a directory with known children as unloaded: "${Q}"`);let Y=x4(this.#X);r9(this.#X,Z),X5(this.#X,h4(this.#X,Y,z0({affectedAncestorIds:n4(this.#X,Z),affectedNodeIds:[Z],path:Q,projectionChanged:this.isDirectoryProjectionVisible(Z)})))})}beginChildLoad(Q){return S(this.#X.instrumentation,"store.beginChildLoad",()=>{let Z=this.requireDirectoryNodeId(Q),Y=x4(this.#X),J=o9(this.#X,Z);return X5(this.#X,h4(this.#X,Y,K0({affectedAncestorIds:n4(this.#X,Z),affectedNodeIds:[Z],attemptId:J.attemptId,path:Q,projectionChanged:this.isDirectoryProjectionVisible(Z),reused:J.reused}))),J})}applyChildPatch(Q,Z){return S(this.#X.instrumentation,"store.applyChildPatch",()=>{let Y=this.resolveActiveDirectoryNodeId(Q.nodeId);if(Y==null||N5(this.#X,Y)!=="loading"||!n9(this.#X,Y,Q.attemptId))return!1;let J=A4(this.#X,Y);this.validateChildPatch(J,Z);let W=x4(this.#X),G=[];for(let U of Z.operations){OQ(J,U);let A=x4(this.#X);switch(U.type){case"add":G.push(h4(this.#X,A,J8(this.#X,U.path)));break;case"remove":G.push(h4(this.#X,A,W8(this.#X,U.path,{recursive:U.recursive})));break;case"move":{let M=G8(this.#X,U.from,U.to,{collision:U.collision});if(M!=null)G.push(h4(this.#X,A,M));break}}}let q=G.some((U)=>U.projectionChanged)||this.isDirectoryProjectionVisible(Y);return X5(this.#X,h4(this.#X,W,M0({affectedAncestorIds:n4(this.#X,Y),affectedNodeIds:[Y],attemptId:Q.attemptId,childEvents:G,path:A4(this.#X,Y),projectionChanged:q}))),!0})}completeChildLoad(Q){return S(this.#X.instrumentation,"store.completeChildLoad",()=>{let Z=this.resolveActiveDirectoryNodeId(Q.nodeId);if(Z==null)return!1;let Y=x4(this.#X),J=a9(this.#X,Z,Q.attemptId);return X5(this.#X,h4(this.#X,Y,H0({affectedAncestorIds:n4(this.#X,Z),affectedNodeIds:[Z],attemptId:Q.attemptId,path:A4(this.#X,Z),projectionChanged:this.isDirectoryProjectionVisible(Z),stale:!J}))),J})}failChildLoad(Q,Z){return S(this.#X.instrumentation,"store.failChildLoad",()=>{let Y=this.resolveActiveDirectoryNodeId(Q.nodeId);if(Y==null)return!1;let J=x4(this.#X),W=t9(this.#X,Y,Q.attemptId,Z);return X5(this.#X,h4(this.#X,J,A0({affectedAncestorIds:n4(this.#X,Y),affectedNodeIds:[Y],attemptId:Q.attemptId,errorMessage:Z,path:A4(this.#X,Y),projectionChanged:this.isDirectoryProjectionVisible(Y),stale:!W}))),W})}cleanup(Q={}){return S(this.#X.instrumentation,"store.cleanup",()=>{if(this.#X.transactionStack.length>0)throw Error("Cleanup cannot run during an open batch or transaction.");if(b0(this.#X))throw Error("Cleanup cannot run while directory loads are active.");let Z=x4(this.#X),Y=S0(this.#X,Q.mode??"stable");return X5(this.#X,h4(this.#X,Z,L0({...Y,affectedAncestorIds:[],affectedNodeIds:[],projectionChanged:Y.idsPreserved===!1}))),Y})}getNodeCount(){return this.#X.activeNodeCount}initializeExpandedPaths(Q){if(Q==null||Q.length===0)return 0;let Z=0,Y=[],J=[],W=0,G=null,q=this.#X.snapshot.segmentTable,U=q.valueById,A=this.#X.snapshot.nodes,M=new Map;for(let O of Q){if(G!=null&&O<G)G=null,W=0,Y.length=0,J.length=0;let z=O.length>0&&O.charCodeAt(O.length-1)===47?O.length-1:O.length;if(z===0){G=O,W=z,Y.length=0,J.length=0;continue}let j=0,B=0;if(G!=null){let F=Math.min(z,W),V=!0;for(let k=0;k<F;k+=1){let P=O.charCodeAt(k);if(P!==G.charCodeAt(k)){V=!1;break}if(P===47)j+=1,B=k+1}if(V){if(F===W&&z>F&&O.charCodeAt(F)===47)j+=1,B=F+1;else if(F===z&&W>F&&G.charCodeAt(F)===47)j+=1,B=z+1}j=Math.min(j,J.length)}let R=j===0?this.#X.snapshot.rootId:J[j-1]??this.#X.snapshot.rootId,D=j,b=!0,w=B;while(w<=z){let F=O.indexOf("/",w),V=F===-1||F>z?z:F,k=O.slice(w,V),P=O4(this.#X,R).childIds,h=D===j?Y[D]??0:0,G4=h,z4,d=M.get(k)??d5(k);M.set(k,d);let Y4=(q4,t)=>{for(G4=q4;G4<t;G4+=1){let e=P[G4],E4=A[e],W4=U[E4.nameId];if(W4===k)return z4=e,!0;let B4=g6(I6(q,E4.nameId),d);if(B4>0||B4===0&&W4>k)return!1}return!1};if(!Y4(h,P.length)&&h>0)Y4(0,h);if(z4===void 0){b=!1;break}if(!y(I(this.#X,z4))){b=!1;break}if(Y[D]=G4,J[D]=z4,R=z4,D+=1,V===z)break;w=V+1}if(G=O,W=z,Y.length=D,J.length=D,!b){G=null,W=0,Y.length=0,J.length=0;continue}for(let F=j;F<D;F+=1){let V=J[F];if(V==null)continue;let k=I(this.#X,V);if(y4(this.#X,V,k))continue;w5(this.#X,V,!0,k),Z+=1}}return Z}hasAllDirectoriesExpanded(){for(let Q of this.#X.snapshot.directories.keys()){if(Q===this.#X.snapshot.rootId)continue;let Z=I(this.#X,Q);if(!y4(this.#X,Q,Z))return!1}return!0}requireDirectoryNodeId(Q){let Z=p4(this.#X,Q);if(Z==null)throw Error(`Path does not exist: "${Q}"`);if(!y(I(this.#X,Z)))throw Error(`Path is not a directory: "${Q}"`);return Z}resolveActiveDirectoryNodeId(Q){try{if(!y(I(this.#X,Q)))throw Error(`Node is not a directory: ${String(Q)}`);return Q}catch{return null}}isDirectoryProjectionVisible(Q){let Z=Q;while(Z!==this.#X.snapshot.rootId){let Y=I(this.#X,Z).parentId;if(Y!==this.#X.snapshot.rootId){let J=I(this.#X,Y),W=M5(this.#X,Y);if(!y4(this.#X,Y,J)&&W!==Z)return!1}Z=Y}return!0}validateChildPatch(Q,Z){new X({paths:this.list(Q),presorted:!0,sort:this.#X.snapshot.options.sort}).batch(Z.operations)}};function OQ(X,Q){switch(Q.type){case"add":case"remove":if(!Q.path.startsWith(X)||Q.path===X)throw Error(`Child patch operation must stay within ${X}: "${Q.path}"`);break;case"move":if(!Q.from.startsWith(X)||!Q.to.startsWith(X)||Q.from===X||Q.to===X)throw Error(`Child patch move must stay within ${X}: "${Q.from}" -> "${Q.to}"`);break}}var s0=(X)=>X.startsWith(o7)?X.slice(o7.length):X;function BQ(X){let Q=X.lastIndexOf("/");if(Q<0)return{parentPath:"",baseName:X};return{parentPath:X.slice(0,Q),baseName:X.slice(Q+1)}}function jQ(X,Q){return X===""?Q:`${X}/${Q}`}function i0({files:X,path:Q,isFolder:Z,nextBasename:Y}){let J=s0(Q),W=Y.trim();if(W.length===0)return{error:"Name cannot be empty."};if(W.includes("/"))return{error:'Name cannot include "/".'};let{parentPath:G,baseName:q}=BQ(J);if(W===q)return{nextFiles:X,sourcePath:J,destinationPath:J,isFolder:Z};let U=jQ(G,W),A=Array(X.length),M=new Set;if(!Z){let B=`${U}/`,R=!1;for(let D=0;D<X.length;D++){let b=X[D];if(b!==J&&b.startsWith(B))return{error:`"${U}" already exists.`};let w=b===J?U:b;if(M.has(w))return{error:`"${U}" already exists.`};if(M.add(w),A[D]=w,b===J)R=!0}if(!R)return{error:"Could not find the selected file to rename."};return{nextFiles:A,sourcePath:J,destinationPath:U,isFolder:Z}}let O=`${J}/`,z=`${U}/`,j=0;for(let B=0;B<X.length;B++){let R=X[B],D=R===J||R.startsWith(O);if(!D&&(R===U||R.startsWith(z)))return{error:`"${U}" already exists.`};let b=D?`${U}${R.slice(J.length)}`:R;if(M.has(b))return{error:`"${U}" already exists.`};if(M.add(b),A[B]=b,D)j++}if(j===0)return{error:"Could not find the selected folder to rename."};return{nextFiles:A,sourcePath:J,destinationPath:U,isFolder:Z}}function _Q(X){return X.endsWith("/")}function FQ(X){let Q=X.endsWith("/")?X.slice(0,-1):X,Z=Q.lastIndexOf("/"),Y=Z<0?Q:Q.slice(Z+1);return X.endsWith("/")?`${Y}/`:Y}function VQ(X){let Q=[],Z=new Set;for(let J of X){if(Z.has(J))continue;Z.add(J),Q.push(J)}let Y=new Set;for(let J of Q.toSorted((W,G)=>{if(W.length!==G.length)return W.length-G.length;return W.localeCompare(G)})){let W=(J.endsWith("/")?J.slice(0,-1):J).split("/"),G=!1;for(let q=0;q<W.length-1;q+=1){let U=`${W.slice(0,q+1).join("/")}/`;if(!Y.has(U))continue;G=!0;break}if(G)continue;Y.add(J)}return Q.filter((J)=>Y.has(J))}function o0(X,Q){return Q.includes(X)?VQ(Q):[X]}function r0(X,Q){if(X===Q)return!0;if(X==null||Q==null)return!1;return X.kind===Q.kind&&X.directoryPath===Q.directoryPath&&X.flattenedSegmentPath===Q.flattenedSegmentPath&&X.hoveredPath===Q.hoveredPath}function H8(X,Q){return{draggedPaths:X,target:Q}}function A8(X,Q){if(Q.kind!=="directory"||Q.directoryPath==null)return!1;for(let Z of X){if(!_Q(Z))continue;if(Q.directoryPath===Z||Q.directoryPath.startsWith(Z))return!0}return!1}function RQ(X,Q){if(Q.kind==="root"||Q.directoryPath==null)return FQ(X);return Q.directoryPath}function a0(X,Q){let Z=X.map((Y)=>{let J=RQ(Y,Q);if(J===Y)return null;return{from:Y,to:J,type:"move"}}).filter((Y)=>{return Y!=null});if(Z.length===0)return null;return{operations:Z,result:{draggedPaths:X,operation:Z.length===1?"move":"batch",target:Q}}}var B8=Symbol("FILE_TREE_RENAME_VIEW");function n0(X){return X.operation==="add"||X.operation==="remove"||X.operation==="move"||X.operation==="batch"}var EQ=512,DQ=512;function L8(X,Q){if(X.size!==Q.length)return!1;for(let Z of Q)if(!X.has(Z))return!1;return!0}function b5(X){let Q=X.endsWith("/")?X.slice(0,-1):X;if(Q.length===0)return[];let Z=Q.split("/");return Z.slice(0,-1).map((Y,J)=>`${Z.slice(0,J+1).join("/")}/`)}function O8(X){return b5(X).at(-1)??null}function t0(X,Q){if(Q==null)return X;return X.startsWith(Q)?X.slice(Q.length):X}var kQ=(X)=>{let Q=X.trim();if(Q.length===0)return"";return(Q.includes("\\")?Q.replaceAll("\\","/"):Q).toLowerCase()},e0=(X)=>X.toLowerCase();function E7(X){return X.endsWith("/")}function TQ(X){let Q=X.endsWith("/")?X.slice(0,-1):X,Z=Q.lastIndexOf("/");return Z<0?Q:Q.slice(Z+1)}function X1(X){return X.endsWith("/")?X.slice(0,-1):X}function Q1(X,Q){return Q&&!X.endsWith("/")?`${X}/`:X}function wQ(X,Q,Z){if(X===Q)return Z;let Y=Q.endsWith("/")?Q:`${Q}/`;if(!X.startsWith(Y))return X;return`${Z.endsWith("/")?Z:`${Z}/`}${X.slice(Y.length)}`}function NQ(X,Q){if(X===Q)return!0;let Z=Q.endsWith("/")?Q:`${Q}/`;return X.startsWith(Z)}function h6(X,Q,Z=!1){if(X==null)return null;switch(Q.operation){case"add":case"expand":case"collapse":case"mark-directory-unloaded":case"begin-child-load":case"apply-child-patch":case"complete-child-load":case"fail-child-load":case"cleanup":return X;case"remove":return NQ(X,Q.path)?Z?X:null:X;case"move":return wQ(X,Q.from,Q.to);case"batch":{let Y=X;for(let J of Q.events)if(Y=h6(Y,J,Z),Y==null)return null;return Y}}}function D7(X){return{canonicalChanged:X.canonicalChanged,projectionChanged:X.projectionChanged,visibleCountDelta:X.visibleCountDelta}}function CQ(X,Q){if(X===Q)return!0;if(X.length!==Q.length)return!1;for(let Z=0;Z<X.length;Z+=1)if(X[Z]!==Q[Z])return!1;return!0}function Z1(X,Q,Z){let{paths:Y,preparedInput:J}=X;if(J==null){if(Y==null)throw Error("FileTree requires paths or preparedInput");return{paths:Y,preparedInput:void 0}}let W=J.paths;if(Y==null)return{paths:W,preparedInput:J};if(!CQ(M8.preparePaths(Y,Z==null?{}:{sort:Z}),W))throw Error(`FileTree ${Q} received paths and preparedInput for different path lists`);return{paths:W,preparedInput:J}}function Y1(X){switch(X.operation){case"add":return{...D7(X),operation:"add",path:X.path};case"remove":return{...D7(X),operation:"remove",path:X.path,recursive:X.recursive};case"move":return{...D7(X),from:X.from,operation:"move",to:X.to}}}function vQ(X){return{...D7(X),events:X.events.filter((Q)=>Q.operation==="add"||Q.operation==="remove"||Q.operation==="move").map((Q)=>Y1(Q)),operation:"batch"}}function bQ(X){switch(X.operation){case"add":case"remove":case"move":return Y1(X);case"batch":return vQ(X);default:return null}}function SQ(X,Q,Z){if(X===0)return-1;if(Z!=null){let Y=Q(Z);if(Y!=null)return Y;let J=b5(Z);for(let W=J.length-1;W>=0;W-=1){let G=J[W];if(G==null)continue;let q=Q(G);if(q!=null)return q}}return 0}function PQ(X,Q,Z){if(X.paths.length===0)return{focusedIndex:-1,getParentIndex:X.getParentIndex,paths:X.paths,posInSetByIndex:X.posInSetByIndex,setSizeByIndex:X.setSizeByIndex};if(Q==null)return{focusedIndex:0,getParentIndex:X.getParentIndex,paths:X.paths,posInSetByIndex:X.posInSetByIndex,setSizeByIndex:X.setSizeByIndex};let Y=Z??((J)=>X.visibleIndexByPath.get(J)??null);return{focusedIndex:SQ(X.paths.length,Y,Q),getParentIndex:X.getParentIndex,paths:X.paths,posInSetByIndex:X.posInSetByIndex,setSizeByIndex:X.setSizeByIndex}}var J1=class{#X;#Z=new Set;#U=new Map;#z=null;#G=null;#x=new Map;#g=new Map;#O=-1;#Y=null;#B=!1;#w=(X)=>-1;#j=new Map;#H=null;#_=null;#F=null;#V=null;#M=null;#I;#m;#P;#J=[];#u=new Int32Array(0);#h=new Int32Array(0);#t=void 0;#C=!1;#q=null;#L="";#N=!1;#D=new Set;#s=[];#p;#c=null;#$=null;#f=null;#l=null;#k=null;#i=null;#R=null;#W=new Set;#o=0;#Q;#G4=0;#Q4=!1;#A=0;#r;constructor(X){let{dragAndDrop:Q,fileTreeSearchMode:Z,initialSearchQuery:Y,initialSelectedPaths:J,renaming:W,onSearchChange:G,paths:q,preparedInput:U,...A}=X,M=Z1({paths:q,preparedInput:U},"constructor",A.sort);if(this.#X=A,Q!=null&&Q!==!1)this.#z=Q===!0?{}:Q;if(this.#C=W!=null&&W!==!1,W!=null&&W!==!1&&W!==!0)this.#t=W.canRename,this.#m=W.onError,this.#I=W.onRename;this.#P=G,this.#p=Z??"hide-non-matches",this.#Q=this.#Y4(M.paths,M.preparedInput);let O=J?.map((j)=>this.#v(j)).filter((j)=>j!=null)??[],z=O.at(-1)??null;if(O.length>0)this.#W=new Set(O),this.#R=z,this.#o=1;if(this.#y(z,!1),Y!=null)this.#a(Y,!1);this.#r=this.#R4()}destroy(){this.#r?.(),this.#r=null,this.#U.clear(),this.#Z.clear(),this.#j.clear(),this.#G=null,this.#W4()}focusFirstItem(){if(this.#T().length>0)this.#b(0)}focusLastItem(){if(this.#A<=0)return;this.#S(),this.#b(this.#A-1)}focusNextItem(){this.#F4(1)}focusParentItem(){if(this.#Y==null)return;let X=O8(this.#Y);if(X==null)return;let Q=this.#d(X);if(Q>=0)this.#b(Q)}focusPath(X){let Q=this.#Q.getPathInfo(X)?.path??null;if(Q==null)return;this.#S();let Z=this.#d(Q);if(Z>=0)this.#b(Z)}focusNearestPath(X){let Q=this.resolveNearestVisiblePath(X);if(Q==null)return null;let Z=this.#d(Q);if(Z>=0)return this.#b(Z),this.#T()[Z]??Q;return null}focusPreviousItem(){this.#F4(-1)}getFocusedIndex(){return this.#O}getFocusedItem(){return this.#Y==null?null:this.#q4(this.#Y)}getFocusedPath(){return this.#Y}resolveNearestVisiblePath(X){let Q=this.#T();if(this.#A===0)return null;if(X==null)return this.#Y??Q[0]??null;let Z=this.#Q.getPathInfo(X)?.path??X,Y=this.#d(Z);if(Y>=0)return Q[Y]??Z;let J=this.#T4(Z);if(J!=null)return J;return this.#Y??Q[0]??null}getSelectedPaths(){return[...this.#W]}getSelectionVersion(){return this.#o}getVisibleCount(){return this.#A}getVisibleRows(X,Q){if(Q<X||this.#A===0)return[];let Z=Math.max(0,X),Y=Math.min(this.#A-1,Q);if(Y<Z)return[];let J=Y-Z+1;if(this.#k==null&&!this.#B&&Y>=this.#J.length&&J<=DQ){let W=[];for(let G=Z;G<=Y;G+=1){let q=this.#Q.getVisibleRowContext(G);if(q==null)break;W.push(this.#$4(q))}return W}if(!this.#B&&Y>=this.#J.length)this.#S();if(this.#k!=null){let W=Array.from({length:Y-Z+1},(A,M)=>this.#L4(Z+M)),G=new Map,q=W[0]??-1,U=q;for(let A=1;A<=W.length;A+=1){let M=W[A];if(M!=null&&M===U+1){U=M;continue}if(q>=0)this.#Q.getVisibleSlice(q,U).forEach((O,z)=>{G.set(q+z,O)});if(M==null){q=-1,U=-1;continue}q=M,U=M}return Array.from({length:Y-Z+1},(A,M)=>{let O=Z+M,z=this.#L4(O),j=G.get(z),B=this.#J[z];if(j==null||B==null)throw Error(`Missing projection row for filtered visible index ${String(O)}`);return this.#Z4(j,O,z,{ancestorPaths:this.#K4(z),path:B})})}return this.#Q.getVisibleSlice(Z,Y).map((W,G)=>{let q=Z+G,U=this.#J[q];if(U==null)throw Error(`Missing projection path for visible index ${String(q)}`);return this.#Z4(W,q,q,{ancestorPaths:this.#K4(q),path:U})})}getStickyRowCandidates(X,Q){if(this.#k!=null)return null;if(this.#A===0||X<=0||Q<=0)return[];let Z=[];for(let Y=0;Y<this.#A;Y+=1){let J=X+Y*Q,W=Math.min(this.#A-1,Math.floor(J/Q)),G=this.#U4(W,Y)??(W>0?this.#U4(W-1,Y):void 0);if(G==null)break;Z.push({row:this.#$4(G),subtreeEndIndex:G.subtreeEndIndex})}return Z}getItem(X){let Q=this.#Q.getPathInfo(X);return Q==null?null:this.#q4(Q.path,Q)}selectAllVisiblePaths(){this.#S();let X=[...this.#T()];this.#E(X,this.#Y??this.#R)}selectOnlyPath(X){let Q=this.#v(X);if(Q==null)return;this.#E([Q],Q)}selectPath(X){let Q=this.#v(X);if(Q==null||this.#W.has(Q))return;this.#E([...this.#W,Q])}deselectPath(X){let Q=this.#v(X);if(Q==null||!this.#W.has(Q))return;this.#E([...this.#W].filter((Z)=>Z!==Q))}toggleFocusedSelection(){if(this.#Y==null)return;this.togglePathSelectionFromInput(this.#Y)}togglePathSelection(X){let Q=this.#v(X);if(Q==null)return;if(this.#W.has(Q)){this.deselectPath(Q);return}this.selectPath(Q)}togglePathSelectionFromInput(X){let Q=this.#v(X);if(Q==null)return;if(this.#W.has(Q)){this.#E([...this.#W].filter((Z)=>Z!==Q),Q);return}this.#E([...this.#W,Q],Q)}selectPathRange(X,Q){let Z=this.#v(X);if(Z==null)return;this.#S();let Y=this.#R,J=Y==null?-1:this.#X4(Y),W=this.#X4(Z);if(J===-1||W===-1){let M=Q?[...this.#W,Z]:[Z];this.#E(M,Z);return}let[G,q]=J<=W?[J,W]:[W,J],U=this.#T().slice(G,q+1),A=Q?[...this.#W,...U]:U;this.#E(A,Y)}extendSelectionFromFocused(X){if(this.#Y==null)return;let Q=this.#O;if(Q===-1)return;let Z=Math.min(this.#A-1,Math.max(0,Q+X));if(Z===Q)return;if(!this.#B&&Z>=this.#J.length)this.#S();let Y=this.#T(),J=Y[Q]??null,W=Y[Z]??null;if(J==null||W==null)return;let G=new Set(this.#W);if(G.has(J)&&G.has(W))G.delete(J);else G.add(W);this.#E([...G],this.#R??J,!1),this.#b(Z)}getDragAndDropConfig(){return this.#z}isDragAndDropEnabled(){return this.#z!=null}getDragSession(){if(this.#G==null)return null;return{draggedPaths:[...this.#G.draggedPaths],primaryPath:this.#G.primaryPath,target:this.#G.target==null?null:{...this.#G.target}}}startDrag(X){if(this.#z==null)return!1;let Q=this.#v(X);if(Q==null)return!1;if(this.#$!=null&&this.#$.length>0)return!1;let Z=this.getSelectedPaths(),Y=o0(Q,Z);if(this.#z.canDrag?.(Y)===!1)return!1;if(!Z.includes(Q))this.#E([Q],Q,!1);return this.#n(Q),this.#G={draggedPaths:Y,primaryPath:Q,target:null},this.#K(),!0}setDragTarget(X){let Q=this.#G;if(Q==null)return;let Z=X;if(Z!=null){let Y=H8(Q.draggedPaths,Z);if(A8(Q.draggedPaths,Z)||this.#z?.canDrop?.(Y)===!1)Z=null}if(r0(Q.target,Z))return;this.#G={...Q,target:Z},this.#K()}cancelDrag(){if(this.#G==null)return;this.#G=null,this.#K()}completeDrag(){let X=this.#G;if(X==null)return!1;this.#G=null;let Q=X.target==null?null:{...X.target};if(Q==null)return this.#K(),!1;let Z=H8(X.draggedPaths,Q);if(A8(X.draggedPaths,Q)||this.#z?.canDrop?.(Z)===!1)return this.#K(),!1;let Y=a0(X.draggedPaths,Q);if(Y==null)return this.#K(),!1;try{if(Y.operations.length===1){let J=Y.operations[0];if(J==null||J.type!=="move")throw Error("Expected a single move operation for one-item drops");this.#Q.move(J.from,J.to,{collision:J.collision})}else this.#C4(Y.operations),this.#Q.batch(Y.operations)}catch(J){return this.#K(),this.#z?.onDropError?.(J instanceof Error?J.message:String(J),Z),!1}return this.#z?.onDropComplete?.(Y.result),!0}subscribe(X){return this.#Z.add(X),X(),()=>{this.#Z.delete(X)}}add(X){this.#Q.add(X)}remove(X,Q={}){this.#Q.remove(X,Q)}move(X,Q,Z={}){this.#Q.move(X,Q,Z)}batch(X){this.#Q.batch(X)}onMutation(X,Q){let Z=X,Y=Q,J=this.#U.get(Z);if(J==null)J=new Set,this.#U.set(Z,J);return J.add(Y),()=>{let W=this.#U.get(Z);if(W?.delete(Y),W?.size===0)this.#U.delete(Z)}}setSearch(X){this.#a(X,!0)}openSearch(X=""){this.#a(X,!0)}closeSearch(){this.#a(null,!0)}isSearchOpen(){return this.#$!==null}getSearchValue(){return this.#$??""}getSearchMatchingPaths(){return this.#s}focusNextSearchMatch(){this.#O4(1)}focusPreviousSearchMatch(){this.#O4(-1)}startRenaming(X=this.#Y??"",Q={}){if(!this.#C)return!1;let Z=this.#Q.getPathInfo(X);if(Z==null)return!1;let Y=Z.path,J=E7(Y),W=X1(Y);if(this.#t?.({isFolder:J,path:W})===!1)return!1;for(let G of b5(Y))if(!this.#Q.isExpanded(G))this.#Q.expand(G);if(this.#E([Y],Y,!1),this.#$!=null)this.#a(null,!1),this.#P?.(this.#$);return this.#n(Y),this.#q=Y,this.#L=TQ(Y),this.#N=Q.removeIfCanceled??!1,this.#K(),!0}[B8](){return{cancel:()=>{this.#E4()},commit:()=>{this.#D4()},getPath:()=>this.#q,getValue:()=>this.#L,isActive:()=>this.#q!=null,setValue:(X)=>{this.#k4(X)}}}#E4(){if(this.#q==null)return;let X=this.#q,Q=this.#N;if(this.#q=null,this.#L="",this.#N=!1,Q){this.remove(X,E7(X)?{recursive:!0}:void 0);return}this.#n(X),this.#K()}#D4(){let X=this.#q;if(X==null)return;if(this.#N&&this.#L.trim().length===0){this.#q=null,this.#L="",this.#N=!1,this.remove(X,E7(X)?{recursive:!0}:void 0);return}let Q=E7(X),Z=i0({files:this.#Q.list(),isFolder:Q,nextBasename:this.#L,path:X1(X)});if(this.#q=null,this.#L="",this.#N=!1,"error"in Z){this.#n(X),this.#m?.(Z.error),this.#K();return}if(Z.sourcePath===Z.destinationPath){this.#n(X),this.#K();return}this.#I?.({destinationPath:Z.destinationPath,isFolder:Z.isFolder,sourcePath:Z.sourcePath}),this.move(Q1(Z.sourcePath,Q),Q1(Z.destinationPath,Q))}#k4(X){if(this.#q==null||this.#L===X)return;this.#L=X,this.#K()}resetPaths(X,Q={}){let Z=this.#Q.list().length,Y=this.#A,J=Z1({paths:X,preparedInput:Q.preparedInput},"resetPaths",this.#X.sort),W=this.#Y4(J.paths,J.preparedInput,Q.initialExpandedPaths),G=this.#Y,q=this.#q,U=this.getSelectedPaths(),A=this.#R;this.#r?.(),this.#Q=W,this.#j.clear(),this.#W4();let M=U.map((z)=>W.getPathInfo(z)?.path??null).filter((z)=>z!=null),O=!L8(this.#W,M);if(this.#W=new Set(M),O)this.#o+=1;if(this.#R=A==null?null:W.getPathInfo(A)?.path??null,this.#q=q==null?null:W.getPathInfo(q)?.path??null,this.#q==null)this.#L="",this.#N=!1;this.#y(G,G!=null||M.length>0||this.#R!=null),this.#r=this.#R4(),this.#K(),this.#j4({canonicalChanged:!0,operation:"reset",pathCountAfter:J.paths.length,pathCountBefore:Z,projectionChanged:!0,usedPreparedInput:Q.preparedInput!=null,visibleCountDelta:this.#A-Y})}#T4(X){this.#S();let Q=O8(X),Z=t0(X,Q),Y=null,J=null;for(let W of this.#T()){if(O8(W)!==Q)continue;let G=t0(W,Q);if(G<Z){Y=W;continue}if(G>Z){J=W;break}}return Y??J}#d(X){let Q=this.#X4(X);if(Q!==-1)return Q;let Z=b5(X);for(let Y=Z.length-1;Y>=0;Y-=1){let J=Z[Y];if(J==null)continue;let W=this.#X4(J);if(W!==-1)return W}return this.#T().length>0?0:-1}#q4(X,Q){let Z=this.#j.get(X);if(Z!=null)return Z;let Y=Q??this.#Q.getPathInfo(X);if(Y==null)return null;let J=Y.kind==="directory"?this.#w4(Y.path):this.#N4(Y.path);return this.#j.set(Y.path,J),J}#Z4(X,Q,Z,Y){return{ancestorPaths:Y.ancestorPaths,depth:X.depth,flattenedSegments:X.flattenedSegments?.map((J)=>({isTerminal:J.isTerminal,name:J.name,path:J.path})),hasChildren:X.hasChildren,index:Q,isExpanded:X.isExpanded,isFlattened:X.isFlattened,isFocused:Y.path===this.#Y,isSelected:this.#W.has(Y.path),kind:X.kind,level:X.depth,name:X.name,path:Y.path,posInSet:Y.posInSet??this.#u[Z]??0,setSize:Y.setSize??this.#h[Z]??0}}#$4(X){return this.#Z4(X.row,X.index,X.index,{ancestorPaths:X.ancestorPaths,path:X.row.path,posInSet:X.posInSet,setSize:X.setSize})}#U4(X,Q){let Z=this.#Q.getVisibleRowContext(X);if(Z==null)return;let Y=Z.ancestorRows[Q];if(Y!=null)return Y;return Q===Z.ancestorRows.length&&Z.row.kind==="directory"&&Z.row.isExpanded?Z:void 0}#z4(X){let Q=this.#x.get(X);if(Q!=null)return Q;let Z=this.#w(X),Y=Z<0?[]:[...this.#z4(Z),Z];return this.#x.set(X,Y),Y}#K4(X){let Q=this.#g.get(X);if(Q!=null)return Q;let Z=this.#z4(X).map((Y)=>this.#J[Y]??"").filter((Y)=>Y!=="");return this.#g.set(X,Z),Z}#M4(X){this.#Q.collapse(X)}#E(X,Q=this.#R,Z=!0){let Y=[...new Set(X)],J=!L8(this.#W,Y),W=this.#R!==Q;if(!J&&!W)return;if(this.#W=new Set(Y),this.#R=Q,J)this.#o+=1;if(Z)this.#K()}#w4(X){return{collapse:()=>{this.#M4(X)},deselect:()=>{this.deselectPath(X)},expand:()=>{this.#_4(X)},focus:()=>{this.focusPath(X)},getPath:()=>X,isDirectory:()=>!0,isExpanded:()=>this.#Q.isExpanded(X),isFocused:()=>this.#Y===X,isSelected:()=>this.#W.has(X),select:()=>{this.selectPath(X)},toggleSelect:()=>{this.togglePathSelection(X)},toggle:()=>{this.#x4(X)}}}#N4(X){return{deselect:()=>{this.deselectPath(X)},focus:()=>{this.focusPath(X)},getPath:()=>X,isDirectory:()=>!1,isFocused:()=>this.#Y===X,isSelected:()=>this.#W.has(X),select:()=>{this.selectPath(X)},toggleSelect:()=>{this.togglePathSelection(X)}}}#C4(X){let Q=this.#Q.list();this.#Y4(Q).batch(X)}#Y4(X,Q,Z){return new M8({...this.#X,paths:X,preparedInput:Q==null?void 0:Q,...Z!==void 0?{initialExpandedPaths:Z}:{}})}#J4(){if(this.#V!=null)return this.#V;return this.#V=this.#Q.list(),this.#V}#v4(){if(this.#F!=null)return this.#F;let X=new Set;for(let Q of this.#J4()){X.add(Q);for(let Z of b5(Q))X.add(Z)}return this.#F=[...X].sort(),this.#F}#b4(){if(this.#M!=null)return this.#M;return this.#M=this.#J4().map(e0),this.#M}#e(){if(this.#H!=null)return this.#H;return this.#H=this.#v4().filter((X)=>X.endsWith("/")),this.#H}#S4(){if(this.#_!=null)return this.#_;return this.#_=this.#e().map(e0),this.#_}#W4(){this.#H=null,this.#_=null,this.#F=null,this.#V=null,this.#M=null}#P4(){return this.#e().filter((X)=>this.#Q.isExpanded(X))}#H4(X){let Q=new Set(this.#c??[]);if(X)for(let Z of this.#W)for(let Y of b5(Z))Q.add(Y);this.#A4(Q)}#A4(X){this.#Q4=!0;try{for(let Q of this.#e()){let Z=X.has(Q),Y=this.#Q.isExpanded(Q);if(Z&&!Y)this.#Q.expand(Q);else if(!Z&&Y)this.#Q.collapse(Q)}}finally{this.#Q4=!1}}#f4(){let X=this.#J;if(this.#s=X.filter((J)=>this.#D.has(J)),this.#$==null||this.#$.length===0||this.#p!=="hide-non-matches"||this.#D.size===0){this.#k=null,this.#i=null,this.#l=null,this.#A=this.#G4;return}let Q=[],Z=[],Y=new Map;for(let[J,W]of X.entries()){if(this.#f?.has(W)!==!0)continue;Y.set(W,Z.length),Q.push(J),Z.push(W)}this.#k=Q,this.#i=Z,this.#l=Y,this.#A=Z.length}#T(){return this.#i??this.#J}#L4(X){return this.#k?.[X]??X}#X4(X){let Q=this.#l?.get(X);if(Q!=null)return Q;return this.#Q.getVisibleIndex(X)??-1}#O4(X){let Q=this.#s;if(Q.length===0)return;let Z=this.#Y,Y=Z==null?-1:Q.indexOf(Z),J=Q[Y<0?X>0?0:Q.length-1:Math.min(Q.length-1,Math.max(0,Y+X))];if(J!=null)this.focusPath(J)}#a(X,Q){let Z=X==null?null:kQ(X),Y=this.#$;if(Y===Z)return;if(Y==null&&Z!=null)this.#c=this.#P4();if(this.#$=Z,Z==null)this.#H4(!0),this.#c=null,this.#D.clear(),this.#f=null,this.#y(this.#Y,!0);else if(Z.length===0)this.#H4(!1),this.#D.clear(),this.#f=null,this.#y(this.#Y,!0);else{let J=this.#B4();this.#y(J,!0)}if(Q)this.#P?.(this.#$),this.#K()}#B4(){if(this.#$==null||this.#$.length===0)return this.#D.clear(),this.#Y;let X=this.#$,Q=this.#J4(),Z=this.#b4(),Y=[],J=new Set,W=null;for(let M=0;M<Q.length;M+=1){if(!Z[M].includes(X))continue;let O=Q[M];Y.push(O),J.add(O),W??=O}let G=this.#e(),q=this.#S4();for(let M=0;M<G.length;M+=1){if(!q[M].includes(X))continue;let O=G[M];if(J.has(O))continue;Y.push(O),J.add(O),W??=O}this.#D=J;let U=this.#p==="hide-non-matches"&&Y.length>0?new Set:null;this.#f=U;let A=this.#p==="expand-matches"?new Set(this.#c??[]):new Set;for(let M of Y){if(U!=null)U.add(M);if(M.endsWith("/"))A.add(M);for(let O of b5(M))if(A.add(O),U!=null)U.add(O)}return this.#A4(A),W??this.#Y}#K(){for(let X of this.#Z)X()}#j4(X){this.#U.get(X.operation)?.forEach((Q)=>{Q(X)}),this.#U.get("*")?.forEach((Q)=>{Q(X)})}#_4(X){for(let Q of b5(X)){if(this.#Q.isExpanded(Q))continue;this.#Q.expand(Q)}if(!this.#Q.isExpanded(X))this.#Q.expand(X)}#F4(X){let Q=this.#A;if(Q===0)return;let Z=this.#O===-1?0:this.#O,Y=Math.min(Q-1,Math.max(0,Z+X));if(Y!==Z||this.#O===-1){if(!this.#B&&this.#k==null&&Y>=this.#J.length)this.#S();this.#b(Y)}}#y(X,Q=!0){let Z=this.#Q.getVisibleCount();this.#G4=Z;let Y=PQ(this.#Q.getVisibleTreeProjectionData(Q?void 0:Math.min(Z,EQ)),X,Q?(J)=>this.#Q.getVisibleIndex(J):void 0);this.#x.clear(),this.#g.clear(),this.#B=Y.paths.length>=Z,this.#w=Y.getParentIndex,this.#J=Y.paths,this.#u=Y.posInSetByIndex,this.#h=Y.setSizeByIndex,this.#f4(),this.#O=X==null?this.#T().length>0?0:-1:this.#d(X),this.#Y=this.#O<0?null:this.#V4(this.#O)}#V4(X){let Q=this.#T()[X];if(Q!=null)return Q;if(this.#k!=null)return null;return this.#Q.getVisibleRowContext(X)?.row.path??null}#v(X){return this.#Q.getPathInfo(X)?.path??null}#n(X){if(X==null)return;let Q=this.#d(X);if(Q>=0)this.#b(Q,!1)}#b(X,Q=!0){let Z=this.#V4(X);if(Z==null)return;if(this.#O===X&&this.#Y===Z)return;if(this.#O=X,this.#Y=Z,Q)this.#K()}#S(){if(this.#B)return;this.#y(this.#Y,!0)}#y4(X){let Q=h6(this.#q,X);if(Q==null&&this.#q!=null)this.#L="";this.#q=Q;let Z=h6(this.#Y,X,!0),Y=[...this.#W].map((q)=>h6(q,X)).filter((q)=>q!=null).map((q)=>this.#Q.getPathInfo(q)?.path??null).filter((q)=>q!=null),J=h6(this.#R,X),W=J==null?null:this.#Q.getPathInfo(J)?.path??null,G=[...new Set(Y)];if(!L8(this.#W,G))this.#W=new Set(G),this.#o+=1;return this.#R=W,Z}#R4(){return this.#Q.on("*",(X)=>{if(this.#Q4)return;if(X.canonicalChanged)this.#j.clear(),this.#W4();if(this.#G!=null&&n0(X))this.#G=null;let Q=n0(X)?this.#y4(X):this.#Y,Z=this.#$!=null&&this.#$.length>0?this.#B4():this.#$===""?this.#Y:Q,Y=this.#$!=null||X.operation!=="expand"&&X.operation!=="collapse";this.#y(Z,Y),this.#K();let J=bQ(X);if(J!=null)this.#j4(J)})}#x4(X){if(this.#Q.isExpanded(X)){this.#M4(X);return}this.#_4(X)}};var W1=(X)=>{if(X==null||X.length===0)return"0";let Q=`${X.length}`;for(let Z of X)Q+=`\x00${Z.path}\x00${Z.status}`;return Q};function G1(X){let Q=X.endsWith("/"),Z="",Y=-1;for(let J=0;J<=X.length;J+=1){if(!(X[J]==="/"||J===X.length)){if(Y===-1)Y=J;continue}if(Y===-1)continue;if(Z!=="")Z+="/";Z+=X.slice(Y,J),Y=-1}if(Z==="")return null;return{isDirectory:Q,path:Z}}function fQ(X){let Q=X.endsWith("/")?X.slice(0,-1):X;if(Q.length===0)return[];let Z=Q.split("/");return Z.slice(0,-1).map((Y,J)=>`${Z.slice(0,J+1).join("/")}/`)}function yQ(X,Q){return Q?`${X}/`:X}function j8(X,Q=null){let Z=W1(X==null?void 0:[...X]);if(Z==="0")return null;if(Q?.signature===Z)return Q;let Y=new Map,J=new Set,W=new Set;for(let G of X??[]){let q=G1(G.path);if(q==null)continue;let U=yQ(q.path,q.isDirectory);if(Y.set(U,G.status),G.status==="ignored"&&q.isDirectory)W.add(U);else if(q.isDirectory)W.delete(U);for(let A of fQ(q.path))J.add(A)}return{directoriesWithChanges:J,ignoredDirectoryPaths:W,signature:Z,statusByPath:Y}}var xQ=(X)=>X.trim().toLowerCase(),gQ=(X)=>{return X.split("/").at(-1)??X},IQ=(X)=>{let Q=X.toLowerCase().split("."),Z=[];for(let Y=1;Y<Q.length;Y+=1)Z.push(Q.slice(Y).join("."));return Z};function k7(X,Q){if(typeof X==="string")return{name:X,remappedFrom:Q};return{...X,remappedFrom:Q}}function q1(X){let Q=G6(X),Z=Q.remap,Y=new Map;for(let[q,U]of Object.entries(Q.byFileName??{}))Y.set(q.toLowerCase(),U);let J=new Map;for(let[q,U]of Object.entries(Q.byFileExtension??{}))J.set(xQ(q),U);let W=Object.entries(Q.byFileNameContains??{}).map(([q,U])=>[q.toLowerCase(),U]);return{resolveIcon:(q,U)=>{if(q==="file-tree-icon-file"&&U!=null){let M=gQ(U),O=M.toLowerCase(),z=Y.get(O);if(z!=null)return k7(z,q);for(let[R,D]of W)if(O.includes(R))return k7(D,q);let j=IQ(M);for(let R of j){let D=J.get(R);if(D!=null)return k7(D,q)}let B=L9(Q.set,M,j);if(B!=null&&Q.set!=="none")return{name:H9(B),remappedFrom:q,token:B}}let A=Z?.[q];if(A==null)return{name:q};return k7(A,q)}}}var M4,M1,mQ,i5,$1,C7,H1,A1,R8,_8,F8,uQ,p6={},L1=[],v7=Array.isArray,E8=L1.slice,S5=Object.assign;function D8(X){X&&X.parentNode&&X.remove()}function A6(X,Q,Z){var Y,J,W,G={};for(W in Q)W=="key"?Y=Q[W]:W=="ref"&&typeof X!="function"?J=Q[W]:G[W]=Q[W];return arguments.length>2&&(G.children=arguments.length>3?E8.call(arguments,2):Z),w7(X,G,Y,J,null)}function w7(X,Q,Z,Y,J){var W={type:X,props:Q,key:Z,ref:Y,__k:null,__:null,__b:0,__e:null,__c:null,constructor:void 0,__v:J==null?++M1:J,__i:-1,__u:0};return J==null&&M4.vnode!=null&&M4.vnode(W),W}function $5(X){return X.children}function N7(X,Q){this.props=X,this.context=Q,this.__g=0}function H6(X,Q){if(Q==null)return X.__?H6(X.__,X.__i+1):null;for(var Z;Q<X.__k.length;Q++)if((Z=X.__k[Q])!=null&&Z.__e!=null)return Z.__e;return typeof X.type=="function"?H6(X):null}function O1(X){var Q,Z;if((X=X.__)!=null&&X.__c!=null){for(X.__e=null,Q=0;Q<X.__k.length;Q++)if((Z=X.__k[Q])!=null&&Z.__e!=null){X.__e=Z.__e;break}return O1(X)}}function U1(X){(8&X.__g||!(X.__g|=8)||!i5.push(X)||C7++)&&$1==M4.debounceRendering||(($1=M4.debounceRendering)||queueMicrotask)(hQ)}function hQ(){for(var X,Q,Z,Y,J,W,G,q,U=1;i5.length;)i5.length>U&&i5.sort(H1),X=i5.shift(),U=i5.length,8&X.__g&&(Z=void 0,J=(Y=(Q=X).__v).__e,W=[],G=[],(q=Q.__P)&&((Z=S5({},Y)).__v=Y.__v+1,M4.vnode&&M4.vnode(Z),k8(q,Z,Y,Q.__n,q.namespaceURI,32&Y.__u?[J]:null,W,J==null?H6(Y):J,!!(32&Y.__u),G,q.ownerDocument),Z.__v=Y.__v,Z.__.__k[Z.__i]=Z,_1(W,Z,G),Z.__e!=J&&O1(Z)));C7=0}function B1(X,Q,Z,Y,J,W,G,q,U,A,M,O){var z,j,B,R,D,b,w,F=Y&&Y.__k||L1,V=Q.length;for(U=pQ(Z,Q,F,U,V),z=0;z<V;z++)(B=Z.__k[z])!=null&&(j=B.__i==-1?p6:F[B.__i]||p6,B.__i=z,b=k8(X,B,j,J,W,G,q,U,A,M,O),R=B.__e,B.ref&&j.ref!=B.ref&&(j.ref&&T8(j.ref,null,B),M.push(B.ref,B.__c||R,B)),D==null&&R!=null&&(D=R),(w=!!(4&B.__u))||j.__k===B.__k?U=j1(B,U,X,w):typeof B.type=="function"&&b!==void 0?U=b:R&&(U=R.nextSibling),B.__u&=-7);return Z.__e=D,U}function pQ(X,Q,Z,Y,J){var W,G,q,U,A,M=Z.length,O=M,z=0;for(X.__k=Array(J),W=0;W<J;W++)(G=Q[W])!=null&&typeof G!="boolean"&&typeof G!="function"?(U=W+z,(G=X.__k[W]=typeof G=="string"||typeof G=="number"||typeof G=="bigint"||G.constructor==String?w7(null,G,null,null,null):v7(G)?w7($5,{children:G},null,null,null):G.constructor==null&&G.__b>0?w7(G.type,G.props,G.key,G.ref?G.ref:null,G.__v):G).__=X,G.__b=X.__b+1,q=null,(A=G.__i=cQ(G,Z,U,O))!=-1&&(O--,(q=Z[A])&&(q.__u|=2)),q==null||q.__v==null?(A==-1&&(J>M?z--:J<M&&z++),typeof G.type!="function"&&(G.__u|=4)):A!=U&&(A==U-1?z--:A==U+1?z++:(A>U?z--:z++,G.__u|=4))):X.__k[W]=null;if(O)for(W=0;W<M;W++)(q=Z[W])!=null&&(2&q.__u)==0&&(q.__e==Y&&(Y=H6(q)),V1(q,q));return Y}function j1(X,Q,Z,Y){var J,W;if(typeof X.type=="function"){for(J=X.__k,W=0;J&&W<J.length;W++)J[W]&&(J[W].__=X,Q=j1(J[W],Q,Z,Y));return Q}X.__e!=Q&&(Y&&(Q&&X.type&&!Q.parentNode&&(Q=H6(X)),Z.insertBefore(X.__e,Q||null)),Q=X.__e);do Q=Q&&Q.nextSibling;while(Q!=null&&Q.nodeType==8);return Q}function cQ(X,Q,Z,Y){var J,W,G,q=X.key,U=X.type,A=Q[Z],M=A!=null&&(2&A.__u)==0;if(A===null&&X.key==null||M&&q==A.key&&U==A.type)return Z;if(Y>(M?1:0)){for(J=Z-1,W=Z+1;J>=0||W<Q.length;)if((A=Q[G=J>=0?J--:W++])!=null&&(2&A.__u)==0&&q==A.key&&U==A.type)return G}return-1}function z1(X,Q,Z){Q[0]=="-"?X.setProperty(Q,Z==null?"":Z):X[Q]=Z==null?"":Z}function T7(X,Q,Z,Y,J){var W;X:if(Q=="style")if(typeof Z=="string")X.style.cssText=Z;else{if(typeof Y=="string"&&(X.style.cssText=Y=""),Y)for(Q in Y)Z&&Q in Z||z1(X.style,Q,"");if(Z)for(Q in Z)Y&&Z[Q]==Y[Q]||z1(X.style,Q,Z[Q])}else if(Q[0]=="o"&&Q[1]=="n")W=Q!=(Q=Q.replace(A1,"$1")),(Q=Q.slice(2))[0].toLowerCase()!=Q[0]&&(Q=Q.toLowerCase()),X.__l||(X.__l={}),X.__l[Q+W]=Z,Z?Y?Z.l=Y.l:(Z.l=R8,X.addEventListener(Q,W?F8:_8,W)):X.removeEventListener(Q,W?F8:_8,W);else{if(J=="http://www.w3.org/2000/svg")Q=Q.replace(/xlink(H|:h)/,"h").replace(/sName$/,"s");else if(Q!="width"&&Q!="height"&&Q!="href"&&Q!="list"&&Q!="form"&&Q!="tabIndex"&&Q!="download"&&Q!="rowSpan"&&Q!="colSpan"&&Q!="role"&&Q!="popover"&&Q in X)try{X[Q]=Z==null?"":Z;break X}catch(G){}typeof Z=="function"||(Z==null||Z===!1&&Q[4]!="-"?X.removeAttribute(Q):X.setAttribute(Q,Q=="popover"&&Z==1?"":Z))}}function K1(X){return function(Q){if(this.__l){var Z=this.__l[Q.type+X];if(Q.u==null)Q.u=R8++;else if(Q.u<Z.l)return;return Z(M4.event?M4.event(Q):Q)}}}function k8(X,Q,Z,Y,J,W,G,q,U,A,M){var O,z,j,B,R,D,b,w,F,V,k,P,h,G4,z4,d,Y4,q4,t,e,E4,W4=Q.type;if(Q.constructor!=null)return null;128&Z.__u&&(U=!!(32&Z.__u),Z.__c.__z&&(q=Q.__e=Z.__e=(W=Z.__c.__z)[0],Z.__c.__z=null)),(O=M4.__b)&&O(Q);X:if(typeof W4=="function")try{if(w=Q.props,F="prototype"in W4&&W4.prototype.render,V=(O=W4.contextType)&&Y[O.__c],k=O?V?V.props.value:O.__:Y,Z.__c?2&(z=Q.__c=Z.__c).__g&&(z.__g|=1,b=!0):(F?Q.__c=z=new W4(w,k):(Q.__c=z=new N7(w,k),z.constructor=W4,z.render=dQ),V&&V.sub(z),z.props=w,z.state||(z.state={}),z.context=k,z.__n=Y,j=!0,z.__g|=8,z.__h=[],z._sb=[]),F&&z.__s==null&&(z.__s=z.state),F&&W4.getDerivedStateFromProps!=null&&(z.__s==z.state&&(z.__s=S5({},z.__s)),S5(z.__s,W4.getDerivedStateFromProps(w,z.__s))),B=z.props,R=z.state,z.__v=Q,j)F&&W4.getDerivedStateFromProps==null&&z.componentWillMount!=null&&z.componentWillMount(),F&&z.componentDidMount!=null&&z.__h.push(z.componentDidMount);else{if(F&&W4.getDerivedStateFromProps==null&&w!==B&&z.componentWillReceiveProps!=null&&z.componentWillReceiveProps(w,k),!(4&z.__g)&&z.shouldComponentUpdate!=null&&z.shouldComponentUpdate(w,z.__s,k)===!1||Q.__v==Z.__v){for(Q.__v!=Z.__v&&(z.props=w,z.state=z.__s,z.__g&=-9),Q.__e=Z.__e,Q.__k=Z.__k,Q.__k.some(function(B4){B4&&(B4.__=Q)}),P=0;P<z._sb.length;P++)z.__h.push(z._sb[P]);z._sb=[],z.__h.length&&G.push(z);break X}z.componentWillUpdate!=null&&z.componentWillUpdate(w,z.__s,k),F&&z.componentDidUpdate!=null&&z.__h.push(function(){z.componentDidUpdate(B,R,D)})}if(z.context=k,z.props=w,z.__P=X,z.__g&=-5,h=M4.__r,G4=0,F){for(z.state=z.__s,z.__g&=-9,h&&h(Q),O=z.render(z.props,z.state,z.context),z4=0;z4<z._sb.length;z4++)z.__h.push(z._sb[z4]);z._sb=[]}else do z.__g&=-9,h&&h(Q),O=z.render(z.props,z.state,z.context),z.state=z.__s;while(8&z.__g&&++G4<25);z.state=z.__s,z.getChildContext!=null&&(Y=S5({},Y,z.getChildContext())),F&&!j&&z.getSnapshotBeforeUpdate!=null&&(D=z.getSnapshotBeforeUpdate(B,R)),d=O,O!=null&&O.type===$5&&O.key==null&&(d=F1(O.props.children)),q=B1(X,v7(d)?d:[d],Q,Z,Y,J,W,G,q,U,A,M),Q.__u&=-161,z.__h.length&&G.push(z),b&&(z.__g&=-4)}catch(B4){if(Q.__v=null,U||W!=null)if(B4.then){for(Y4=0,q4=!1,Q.__u|=U?160:128,Q.__c.__z=[],t=0;t<W.length;t++)(e=W[t])==null||q4||(e.nodeType==8&&e.data=="$s"?(Y4>0&&Q.__c.__z.push(e),Y4++,W[t]=null):e.nodeType==8&&e.data=="/$s"?(--Y4>0&&Q.__c.__z.push(e),q4=Y4===0,q=W[t],W[t]=null):Y4>0&&(Q.__c.__z.push(e),W[t]=null));if(!q4){for(;q&&q.nodeType==8&&q.nextSibling;)q=q.nextSibling;W[W.indexOf(q)]=null,Q.__c.__z=[q]}Q.__e=q}else{for(E4=W.length;E4--;)D8(W[E4]);V8(Q)}else Q.__e=Z.__e,Q.__k=Z.__k,B4.then||V8(Q);M4.__e(B4,Q,Z)}else q=Q.__e=lQ(Z.__e,Q,Z,Y,J,W,G,U,A,M);return(O=M4.diffed)&&O(Q),128&Q.__u?void 0:q}function V8(X){X&&X.__c&&(X.__c.__g|=4),X&&X.__k&&X.__k.forEach(V8)}function _1(X,Q,Z){for(var Y=0;Y<Z.length;Y++)T8(Z[Y],Z[++Y],Z[++Y]);M4.__c&&M4.__c(Q,X),X.some(function(J){try{X=J.__h,J.__h=[],X.some(function(W){W.call(J)})}catch(W){M4.__e(W,J.__v)}})}function F1(X){return typeof X!="object"||X==null||X.__b&&X.__b>0?X:v7(X)?X.map(F1):S5({},X)}function lQ(X,Q,Z,Y,J,W,G,q,U,A){var M,O,z,j,B,R,D,b,w=Z.props,F=Q.props,V=Q.type;if(V=="svg"?J="http://www.w3.org/2000/svg":V=="math"?J="http://www.w3.org/1998/Math/MathML":J||(J="http://www.w3.org/1999/xhtml"),W!=null){for(M=0;M<W.length;M++)if((B=W[M])&&"setAttribute"in B==!!V&&(V?B.localName==V:B.nodeType==3)){X=B,W[M]=null;break}}if(X==null){if(V==null)return A.createTextNode(F);X=A.createElementNS(J,V,F.is&&F),q&&(M4.__m&&M4.__m(Q,W),q=!1),W=null}if(V==null)w===F||q&&X.data==F||(X.data=F);else{if(W=W&&E8.call(X.childNodes),w=Z.props||p6,!q&&W!=null)for(w={},M=0;M<X.attributes.length;M++)w[(B=X.attributes[M]).name]=B.value;for(M in w)if(B=w[M],M=="children");else if(M=="dangerouslySetInnerHTML")z=B;else if(!(M in F)){if(M=="value"&&"defaultValue"in F||M=="checked"&&"defaultChecked"in F)continue;T7(X,M,null,B,J)}for(M in b=1&Z.__u,F)B=F[M],M=="children"?j=B:M=="dangerouslySetInnerHTML"?O=B:M=="value"?R=B:M=="checked"?D=B:q&&typeof B!="function"||w[M]===B&&!b||T7(X,M,B,w[M],J);if(O)q||z&&(O.__html==z.__html||O.__html==X.innerHTML)||(X.innerHTML=O.__html),Q.__k=[];else if(z&&(X.innerHTML=""),B1(V=="template"?X.content:X,v7(j)?j:[j],Q,Z,Y,V=="foreignObject"?"http://www.w3.org/1999/xhtml":J,W,G,W?W[0]:Z.__k&&H6(Z,0),q,U,A),W!=null)for(M=W.length;M--;)D8(W[M]);q||(M="value",V=="progress"&&R==null?X.removeAttribute("value"):R==null||R===X[M]&&(V!=="progress"||R)||T7(X,M,R,w[M],J),M="checked",D!=null&&D!=X[M]&&T7(X,M,D,w[M],J))}return X}function T8(X,Q,Z){try{if(typeof X=="function"){var Y=typeof X.__u=="function";Y&&X.__u(),Y&&Q==null||(X.__u=X(Q))}else X.current=Q}catch(J){M4.__e(J,Z)}}function V1(X,Q,Z){var Y,J;if(M4.unmount&&M4.unmount(X),(Y=X.ref)&&(Y.current&&Y.current!=X.__e||T8(Y,null,Q)),(Y=X.__c)!=null){if(Y.componentWillUnmount)try{Y.componentWillUnmount()}catch(W){M4.__e(W,Q)}Y.__P=null}if(Y=X.__k)for(J=0;J<Y.length;J++)Y[J]&&V1(Y[J],Q,Z||typeof X.type!="function");Z||D8(X.__e),X.__e&&X.__e.__l&&(X.__e.__l=null),X.__e=X.__c=X.__=null}function dQ(X,Q,Z){return this.constructor(X,Z)}function b7(X,Q){var Z,Y,J,W;Q==document&&(Q=document.documentElement),M4.__&&M4.__(X,Q),Y=(Z=!!(X&&32&X.__u))?null:Q.__k,X=Q.__k=A6($5,null,[X]),J=[],W=[],k8(Q,X,Y||p6,p6,Q.namespaceURI,Y?null:Q.firstChild?E8.call(Q.childNodes):null,J,Y?Y.__e:Q.firstChild,Z,W,Q.ownerDocument),_1(J,X,W)}function R1(X,Q){X.__u|=32,b7(X,Q)}M4={__e:function(X,Q,Z,Y){for(var J,W,G;Q=Q.__;)if((J=Q.__c)&&!(1&J.__g)){J.__g|=4;try{if((W=J.constructor)&&W.getDerivedStateFromError!=null&&(J.setState(W.getDerivedStateFromError(X)),G=8&J.__g),J.componentDidCatch!=null&&(J.componentDidCatch(X,Y||{}),G=8&J.__g),G)return void(J.__g|=2)}catch(q){X=q}}throw C7=0,X}},M1=0,mQ=function(X){return X!=null&&X.constructor==null},N7.prototype.setState=function(X,Q){var Z;Z=this.__s!=null&&this.__s!=this.state?this.__s:this.__s=S5({},this.state),typeof X=="function"&&(X=X(S5({},Z),this.props)),X&&S5(Z,X),X!=null&&this.__v&&(Q&&this._sb.push(Q),U1(this))},N7.prototype.forceUpdate=function(X){this.__v&&(this.__g|=4,X&&this.__h.push(X),U1(this))},N7.prototype.render=$5,i5=[],C7=0,H1=function(X,Q){return X.__v.__b-Q.__v.__b},A1=/(PointerCapture)$|Capture$/i,R8=0,_8=K1(!1),F8=K1(!0),uQ=0;var sQ=0;function v(X,Q,Z,Y,J,W){Q||(Q={});var G,q,U=Q;if("ref"in U&&typeof X!="function")for(q in U={},Q)q=="ref"?G=Q[q]:U[q]=Q[q];var A={type:X,props:U,key:Z,ref:G,__k:null,__:null,__b:0,__e:null,__c:null,constructor:void 0,__v:--sQ,__i:-1,__u:0,__source:J,__self:W};return M4.vnode&&M4.vnode(A),A}var iQ=16,oQ=16,rQ={};function L6({name:X,remappedFrom:Q,token:Z,width:Y,height:J,viewBox:W,label:G,alignCapitals:q=!1}){let U=`#${X.replace(/^#/,"")}`,{width:A,height:M,viewBox:O}=rQ[X]??{width:iQ,height:oQ},z=Y??A,j=J??M,B=W??O??`0 0 ${A} ${M}`,R=G!=null?{"aria-label":G,role:"img"}:{"aria-hidden":!0};return v("svg",{"data-icon-name":Q??X,"data-icon-token":Z,"data-align-capitals":q,...R,viewBox:B,width:z,height:j,children:v("use",{href:U})})}var E1=(X)=>{if(X.length<2)return[X,""];let Q=Math.ceil(X.length/2);return[X.slice(0,Q),X.slice(Q)]},aQ=(X)=>{if(X.length<4)return[X,""];let Q=X.lastIndexOf(".")+1,Z=X.length-Q>10,Y=Q>=1&&!Z?Q:Math.ceil(X.length/2);return[X.slice(0,Y),X.slice(Y)]},nQ=(X)=>{if(X.length<4)return[X,""];let Q=X.lastIndexOf("/")+1,Z=X.length-Q>25,Y=Q>=1&&!Z?Q:Math.ceil(X.length/2);return[X.slice(0,Y),X.slice(Y)]},tQ=(X,{splitIndex:Q}={})=>{if(typeof Q!=="number"){let Z=Math.ceil(X.length/2);return[X.slice(0,Z),X.slice(Z)]}return[X.slice(0,Q),X.slice(Q)]},eQ=(X,{splitOffset:Q}={})=>{if(typeof Q!=="number"||Q<=0||Q>=X.length){let Y=Math.ceil(X.length/2);return[X.slice(0,Y),X.slice(Y)]}let Z=X.length-Q;return[X.slice(0,Z),X.slice(Z)]},XZ=(X,{splitOffset:Q}={})=>{if(typeof Q!=="number"||Q<=0||Q>=X.length){let Y=Math.ceil(X.length/2);return[X.slice(0,Y),X.slice(Y)]}let Z=Q;return[X.slice(0,Z),X.slice(Z)]};function QZ({children:X,marker:Q,variant:Z="default"}){return v("div",{"aria-hidden":!0,"data-truncate-marker-cell":!0,children:v("div",{"data-truncate-marker":!0,children:typeof Q==="function"?Q({children:X}):Z==="fade"?v("span",{"data-truncate-fade":!0}):Q})})}function ZZ(X){let{mode:Q,children:Z}=X;return v("div",{children:[v("div",{"data-truncate-content":"visible",children:Q==="fruncate"?v("span",{children:Z}):Z}),v("div",{"data-truncate-content":"overflow","aria-hidden":!0,children:Q==="fruncate"?v("span",{children:Z}):Z})]})}function D1({children:X,mode:Q="truncate",marker:Z="…",variant:Y="default",...J}){let W=v(ZZ,{mode:Q,children:X},"content"),G=v(QZ,{marker:Z,mode:Q,variant:Y},"marker");return v("div",{"data-truncate-container":Q,"data-truncate-variant":Y,...J,children:v("div",{"data-truncate-grid":!0,children:Q==="truncate"?[W,G]:[G,W,v("div",{"data-truncate-fill":!0},"fill")]})})}function c6({children:X,...Q}){return v(D1,{mode:"truncate",...Q,children:X})}function w8({children:X,...Q}){return v(D1,{mode:"fruncate",...Q,children:X})}function k1({children:X,contents:Q,priority:Z="end",split:Y="center",minimumLength:J=12,className:W,style:G,...q}){let U=null,A=null;if(Array.isArray(Q)){if(Q.length!==2)return console.error("MiddleTruncate: contents must be an array of two items"),null;U=v(c6,{...q,children:Q[0]}),A=v(w8,{...q,children:Q[1]})}else{if(typeof X!=="string")return console.error("MiddleTruncate: children must be a string"),null;if(X.length===0)return v("div",{className:W,style:G});if(X.length<J)if(Z==="end")return v(w8,{...q,className:W,style:G,children:X});else return v(c6,{...q,className:W,style:G,children:X});let M=null,O=null,z=null;if(typeof Y==="string"){if(Y==="center")M=E1;else if(Y==="extension")M=aQ;else if(Y==="leaf-path")M=nQ}else if(typeof Y==="number")M=tQ,O=Y;else if(Array.isArray(Y)){let[V,k]=Y;if(z=k,V==="last")M=eQ;else if(V==="first")M=XZ}else if(typeof Y==="function")M=Y;M??=E1;let[j,B]=M(X,{priority:Z,variant:q.variant,splitIndex:typeof O==="number"?O:void 0,splitOffset:typeof z==="number"?z:void 0}),R=j.length>=B.length,D=Z==="equal"&&!R,b=Z==="equal"&&R,w={},F={};if(D)w.marker="";if(b)F.marker="";U=v(c6,{...q,...w,children:j}),A=v(w8,{...q,...F,children:B})}return v("div",{"data-truncate-group-container":"middle",className:W,style:G,children:[v("div",{"data-truncate-segment-priority":Z==="start"||Z==="equal"?"1":"2",children:U}),v("div",{"data-truncate-segment-priority":Z==="end"||Z==="equal"?"1":"2",children:A})]})}var N8={endIndex:-1,startIndex:-1};function YZ(X,Q,Z){return Math.min(Math.max(X,Q),Z)}function T1(X,Q){return X<0||Q<X?N8:{endIndex:Q,startIndex:X}}function C8(X){return X.startIndex<0||X.endIndex<X.startIndex}function JZ(X,Q){return C8(X)?0:(X.endIndex-X.startIndex+1)*Q}function w1(X,Q,Z){if(Q<=0)return-1;let Y=Q*Z;if(X<=0)return 0;if(X>=Y)return Q;return Math.floor(X/Z)}function WZ(X,Q,Z){if(Q<=0||X<=0)return-1;if(X>=Q*Z)return Q-1;return Math.ceil(X/Z)-1}function GZ(X){let Q=new Map;return X.forEach((Z,Y)=>{if(Z.kind!=="directory"||!Z.isExpanded)return;let J=Z.ancestorPaths.length,W=Q.get(J);if(W==null){Q.set(J,[Y]);return}W.push(Y)}),Q}function qZ(X,Q){let Z=0,Y=X.length-1,J=-1;while(Z<=Y){let W=Math.floor((Z+Y)/2),G=X[W];if(G==null)break;if(G<=Q){J=W,Z=W+1;continue}Y=W-1}return J}function $Z(X){let Q=new Map,Z=[];for(let J=0;J<X.length;J+=1){let W=X[J];if(W==null)continue;let G=W.kind==="directory"&&W.isExpanded?[...W.ancestorPaths,W.path]:W.ancestorPaths,q=0;while(q<Z.length&&q<G.length&&Z[q]===G[q])q+=1;for(let U=Z.length-1;U>=q;U-=1){let A=Z[U];if(A!=null)Q.set(A,J-1)}Z.length=q;for(let U=q;U<G.length;U+=1){let A=G[U];if(A!=null)Z.push(A)}}let Y=X.length-1;for(let J of Z)Q.set(J,Y);return Q}function v8(X,Q,Z){if(X.length===0||Q<=0)return[];let Y=$Z(X),J=GZ(X),W=[];for(let G=0;G<X.length;G+=1){let q=J.get(G);if(q==null||q.length===0)break;let U=Q+G*Z,A=qZ(q,Math.min(X.length-1,Math.floor(U/Z))),M=null;while(A>=0){let O=q[A],z=O==null?null:X[O]??null;if(z!=null&&(G===0||z.ancestorPaths[G-1]===W[G-1]?.path)){M=z;break}A-=1}if(M==null)break;W.push(M)}return W.map((G,q)=>{let U=q*Z,A=(Y.get(G.path)??X.length-1)+1;if(A>=X.length)return{row:G,top:U};let M=A*Z-Q;return{row:G,top:Math.min(U,M-Z)}}).filter((G)=>G.top+Z>0)}function N1(X,Q){let Z=Q.totalRowCount??X.length,Y=Z*Q.itemHeight,J=Math.max(0,Q.viewportHeight),W=Math.max(0,Math.floor(Q.overscan)),G=Math.max(0,Y-J),q=YZ(Q.scrollTop,0,G),U=Q.stickyRows??v8(X,q,Q.itemHeight),A=U.reduce((P,h)=>Math.max(P,h.top+Q.itemHeight),0),M=Math.min(Y,q+A),O=Math.max(0,J-A),z=Math.max(0,Y-M),j=w1(q,Z,Q.itemHeight),B=w1(M,Z,Q.itemHeight),R=A<=0||j<0||j>=Z?-1:j,D=R===-1?-1:Math.min(Z-1,B-1),b=R===-1||D<R?0:D-R+1,w=O<=0||B>=Z?N8:T1(B,WZ(M+O,Z,Q.itemHeight)),F=D+1,V=C8(w)?N8:T1(Math.max(F,w.startIndex-W),Math.min(Z-1,w.endIndex+W)),k=JZ(V,Q.itemHeight);return{occlusion:{firstOccludedIndex:R,lastOccludedIndex:D,occludedCount:b},physical:{itemHeight:Q.itemHeight,maxScrollTop:G,overscan:W,scrollTop:q,totalHeight:Y,totalRowCount:Z,viewportHeight:J},projected:{contentHeight:z,paneHeight:O,paneTop:M},sticky:{height:A,rows:U},visible:w,window:{endIndex:V.endIndex,height:k,offsetTop:C8(V)?0:V.startIndex*Q.itemHeight,startIndex:V.startIndex}}}var C1={added:"A",deleted:"D",ignored:null,modified:"M",renamed:"R",untracked:"U"},v1={added:"Git status: added",deleted:"Git status: deleted",ignored:"Git status: ignored",modified:"Git status: modified",renamed:"Git status: renamed",untracked:"Git status: untracked"},b1="Contains git status items";function S1(X){let{renamingPath:Q,previousRenamingPath:Z,hasRenderedInput:Y}=X;if(Q==null)return"reset";if(!Y)return"reveal-canonical";if(Z===Q)return"ignore";return"focus-input"}function P1(X){let{row:Q,mode:Z,targetPath:Y,ariaLabel:J,domId:W,isParked:G,itemHeight:q,features:U,state:A,extraStyle:M}=X,O=Z==="sticky",z=Q.ancestorPaths.at(-1)??"",j={};if(A.isFocusRinged)j["data-item-focused"]=!0;if(Q.isSelected)j["data-item-selected"]=!0;if(A.isContextHovered)j["data-item-context-hover"]="true";if(A.isDragTarget)j["data-item-drag-target"]=!0;if(A.isDragging)j["data-item-dragging"]=!0;if(A.effectiveGitStatus!=null)j["data-item-git-status"]=A.effectiveGitStatus;if(A.containsGitChange)j["data-item-contains-git-change"]="true";return{"aria-expanded":!O&&Q.kind==="directory"?Q.isExpanded:void 0,"aria-haspopup":U.contextMenuEnabled?"menu":void 0,"aria-label":J,"aria-level":!O?Q.level+1:void 0,"aria-posinset":!O?Q.posInSet+1:void 0,"aria-selected":!O?Q.isSelected?"true":"false":void 0,"aria-setsize":!O?Q.setSize:void 0,"data-file-tree-sticky-path":O?Y:void 0,"data-file-tree-sticky-row":O?"true":void 0,"data-item-context-menu-button-visibility":U.actionLaneEnabled?U.contextMenuButtonVisibility:void 0,"data-item-context-menu-trigger-mode":U.contextMenuEnabled?U.contextMenuTriggerMode:void 0,"data-item-has-context-menu-action-lane":U.actionLaneEnabled?"true":void 0,"data-item-has-git-lane":U.gitLaneActive?"true":void 0,"data-item-parent-path":z.length>0?z:void 0,"data-item-parked":G?"true":void 0,"data-item-path":Y,"data-item-type":Q.kind==="directory"?"folder":"file","data-type":"item",id:!O?W:void 0,role:!O?"treeitem":void 0,style:{minHeight:`${q}px`,...M},tabIndex:!O&&Q.isFocused?0:-1,...j}}function f1(X){let{event:Q,mode:Z,isSearchOpen:Y,isDirectory:J}=X,W=Q.ctrlKey||Q.metaKey,G=Q.shiftKey||W,q=Q.shiftKey?{additive:W,kind:"range"}:W?{kind:"toggle"}:{kind:"single"};return{closeSearch:Y,revealCanonical:Z==="sticky",selection:q,toggleDirectory:!G&&J}}function y1(X){let{currentScrollTop:Q,focusedIndex:Z,itemHeight:Y,topInset:J=0,viewportHeight:W}=X;if(Z<0)return null;let G=Math.max(0,J),q=Z*Y,U=q+Y;if(q<Q+G){let A=Math.max(0,q-G);return A===Q?null:A}if(U>Q+W){let A=U-W;return A===Q?null:A}return null}function x1(X){let{currentScrollTop:Q,focusedIndex:Z,itemHeight:Y,targetViewportOffset:J,totalHeight:W,viewportHeight:G}=X;if(Z<0)return null;let q=Math.max(0,J),U=Z*Y,A=U+Y,M=Q+q,O=Q+G;if(U>=M&&A<=O)return null;let z=Math.max(0,W-G),j=Math.max(0,Math.min(U-q,z));return j===Q?null:j}var O6,k4,b8,g1,S8=Object.is,l6=0,d1=[],w4=M4,I1=w4.__b,m1=w4.__r,u1=w4.diffed,h1=w4.__c,p1=w4.unmount,c1=w4.__;function P7(X,Q){w4.__h&&w4.__h(k4,X,l6||Q),l6=0;var Z=k4.__H||(k4.__H={__:[],__h:[]});return X>=Z.__.length&&Z.__.push({}),Z.__[X]}function J5(X){return l6=1,UZ(s1,X)}function UZ(X,Q,Z){var Y=P7(O6++,2);if(Y.t=X,!Y.__c&&(Y.__=[Z?Z(Q):s1(void 0,Q),function(q){var U=Y.__N?Y.__N[0]:Y.__[0],A=Y.t(U,q);S8(U,A)||(Y.__N=[A,Y.__[1]],Y.__c.setState({}))}],Y.__c=k4,!k4.__f)){var J=function(q,U,A){if(!Y.__c.__H)return!0;var M=Y.__c.__H.__.filter(function(z){return!!z.__c});if(M.every(function(z){return!z.__N}))return!W||W.call(this,q,U,A);var O=Y.__c.props!==q;return M.forEach(function(z){if(z.__N){var j=z.__[0];z.__=z.__N,z.__N=void 0,S8(j,z.__[0])||(O=!0)}}),W&&W.call(this,q,U,A)||O};k4.__f=!0;var{shouldComponentUpdate:W,componentWillUpdate:G}=k4;k4.componentWillUpdate=function(q,U,A){if(4&this.__g){var M=W;W=void 0,J(q,U,A),W=M}G&&G.call(this,q,U,A)},k4.shouldComponentUpdate=J}return Y.__N||Y.__}function f8(X,Q){var Z=P7(O6++,3);!w4.__s&&y8(Z.__H,Q)&&(Z.__=X,Z.u=Q,k4.__H.__h.push(Z))}function i4(X,Q){var Z=P7(O6++,4);!w4.__s&&y8(Z.__H,Q)&&(Z.__=X,Z.u=Q,k4.__h.push(Z))}function o(X){return l6=5,A5(function(){return{current:X}},[])}function A5(X,Q){var Z=P7(O6++,7);return y8(Z.__H,Q)&&(Z.__=X(),Z.__H=Q,Z.__h=X),Z.__}function I4(X,Q){return l6=8,A5(function(){return X},Q)}function zZ(){for(var X;X=d1.shift();)if(X.__P&&X.__H)try{X.__H.__h.forEach(S7),X.__H.__h.forEach(P8),X.__H.__h=[]}catch(Q){X.__H.__h=[],w4.__e(Q,X.__v)}}w4.__b=function(X){k4=null,I1&&I1(X)},w4.__=function(X,Q){X&&Q.__k&&Q.__k.__m&&(X.__m=Q.__k.__m),c1&&c1(X,Q)},w4.__r=function(X){m1&&m1(X),O6=0;var Q=(k4=X.__c).__H;Q&&(b8===k4?(Q.__h=[],k4.__h=[],Q.__.forEach(function(Z){Z.__N&&(Z.__=Z.__N),Z.u=Z.__N=void 0})):(Q.__h.forEach(S7),Q.__h.forEach(P8),Q.__h=[],O6=0)),b8=k4},w4.diffed=function(X){u1&&u1(X);var Q=X.__c;Q&&Q.__H&&(Q.__H.__h.length&&(d1.push(Q)!==1&&g1===w4.requestAnimationFrame||((g1=w4.requestAnimationFrame)||KZ)(zZ)),Q.__H.__.forEach(function(Z){Z.u&&(Z.__H=Z.u),Z.u=void 0})),b8=k4=null},w4.__c=function(X,Q){Q.some(function(Z){try{Z.__h.forEach(S7),Z.__h=Z.__h.filter(function(Y){return!Y.__||P8(Y)})}catch(Y){Q.some(function(J){J.__h&&(J.__h=[])}),Q=[],w4.__e(Y,Z.__v)}}),h1&&h1(X,Q)},w4.unmount=function(X){p1&&p1(X);var Q,Z=X.__c;Z&&Z.__H&&(Z.__H.__.forEach(function(Y){try{S7(Y)}catch(J){Q=J}}),Z.__H=void 0,Q&&w4.__e(Q,Z.__v))};var l1=typeof requestAnimationFrame=="function";function KZ(X){var Q,Z=function(){clearTimeout(Y),l1&&cancelAnimationFrame(Q),setTimeout(X)},Y=setTimeout(Z,35);l1&&(Q=requestAnimationFrame(Z))}function S7(X){var Q=k4,Z=X.__c;typeof Z=="function"&&(X.__c=void 0,Z()),k4=Q}function P8(X){var Q=k4;X.__c=X.__(),k4=Q}function y8(X,Q){return!X||X.length!==Q.length||Q.some(function(Z,Y){return!S8(Z,X[Y])})}function s1(X,Q){return typeof Q=="function"?Q(X):Q}function j6(X){if(X==null||!X.isConnected)return!1;if(X===document.body||X===document.documentElement)return!1;X.focus({preventScroll:!0});let Q=X.getRootNode();if(Q instanceof ShadowRoot)return Q.activeElement===X;return document.activeElement===X}function f7(X){let Q=X.getRootNode();if(Q instanceof ShadowRoot){let Y=Q.activeElement;return Y instanceof HTMLElement?Y:null}let Z=document.activeElement;return Z instanceof HTMLElement&&X.contains(Z)?Z:null}function MZ({ariaLabel:X,isFlattened:Q=!1,ref:Z,value:Y,onBlur:J,onInput:W}){return v("input",{ref:Z,"data-item-rename-input":!0,...Q?{"data-item-flattened-rename-input":!0}:{},"aria-label":X,value:Y,onBlur:J,onInput:W,onClick:(G)=>G.stopPropagation(),onMouseDown:(G)=>G.stopPropagation(),onPointerDown:(G)=>G.stopPropagation()})}function HZ(X,Q=null,Z=null){let Y=X.flattenedSegments;if(Y==null||Y.length===0)return Q??X.name;return v("span",{"data-item-flattened-subitems":!0,children:Y.map((J,W)=>{let G=W===Y.length-1;return v($5,{children:[v("span",{"data-item-flattened-subitem":J.path,"data-item-flattened-subitem-drag-target":Z===J.path?"true":void 0,children:G&&Q!=null?Q:v(c6,{children:J.name})}),W<Y.length-1?" / ":""]},J.path)})})}function _6(X){return X.isFlattened?X.flattenedSegments?.findLast((Q)=>Q.isTerminal)?.path??X.path:X.path}function I8(X){let Q=X.flattenedSegments;if(Q==null||Q.length===0)return X.name;return Q.map((Z)=>Z.name).join(" / ")}function i1(X,Q,Z,Y){return X.map((J,W)=>{let G=W*Z,q=J.subtreeEndIndex+1;if(q>=Y)return{row:J.row,top:G};let U=q*Z-Q;return{row:J.row,top:Math.min(G,U-Z)}}).filter((J)=>J.top+Z>0)}function x8({controller:X,itemHeight:Q,overscan:Z,scrollTop:Y,stickyFolders:J,viewportHeight:W}){let G=X.getVisibleCount(),q=J&&G>0?X.getStickyRowCandidates(Y,Q):[],U=q==null&&J&&G>0?X.getVisibleRows(0,G-1):[],A=N1(U,{itemHeight:Q,overscan:Z,scrollTop:Y,stickyRows:q==null?void 0:i1(q,Y,Q,G),totalRowCount:G,viewportHeight:W}),M=J&&Y<=0&&G>0?X.getStickyRowCandidates(1,Q):[],O=M!=null&&Y<=0?i1(M,1,Q,G):J&&Y<=0&&U.length>0?v8(U,1,Q):A.sticky.rows;return{overlayHeight:O.reduce((z,j)=>Math.max(z,j.top+Q),0),overlayRows:O,snapshot:A,visibleRows:U}}var AZ=400,o1=10,B6=40,r1=18;function LZ(X,Q,Z){let Y=X,J=document.elementFromPoint?.bind(document)??null,W=Y.elementFromPoint?.(Q,Z)??J?.(Q,Z)??null;if(X instanceof ShadowRoot&&(W==null||!X.contains(W)))return OZ(X,Q,Z);return W instanceof HTMLElement?W:null}function OZ(X,Q,Z){let Y=Array.from(X.querySelectorAll('[data-type="item"], [data-item-flattened-subitem]'));for(let J=Y.length-1;J>=0;J--){let W=Y[J],G=W.getBoundingClientRect();if(Q>=G.left&&Q<=G.right&&Z>=G.top&&Z<=G.bottom)return W}return null}function a1(X){let Q=X?.closest?.('[data-type="item"]');if(!(Q instanceof HTMLElement))return null;let Z=Q.dataset.itemPath??null;if(Z==null)return null;let Y=X?.closest?.("[data-item-flattened-subitem]"),J=Y instanceof HTMLElement?Y.getAttribute("data-item-flattened-subitem")??null:null;if(J!=null&&J.endsWith("/"))return{directoryPath:J,flattenedSegmentPath:J,hoveredPath:Z,kind:"directory"};if(Q.dataset.itemType==="folder")return{directoryPath:Z,flattenedSegmentPath:null,hoveredPath:Z,kind:"directory"};let W=Q.dataset.itemParentPath??null;if(W==null||W.length===0)return{directoryPath:null,flattenedSegmentPath:null,hoveredPath:Z,kind:"root"};return{directoryPath:W,flattenedSegmentPath:null,hoveredPath:Z,kind:"directory"}}function n1(X){let Q=X.cloneNode(!0);return Q.removeAttribute("id"),Q.dataset.fileTreeDragPreview="true",Q.setAttribute("aria-hidden","true"),Q.tabIndex=-1,Object.assign(Q.style,{boxShadow:"0 4px 12px rgba(0, 0, 0, 0.15)",left:"0px",margin:"0",pointerEvents:"none",position:"fixed",top:"0px",willChange:"transform",zIndex:"10000"}),Q}function BZ(){return navigator.vendor!=="Apple Computer, Inc."}function jZ(X,Q){let Z=X-Q.top;if(Z<B6){let J=Math.max(0,Z);return-Math.ceil((B6-J)/B6*r1)}let Y=Q.bottom-X;if(Y<B6){let J=Math.max(0,Y);return Math.ceil((B6-J)/B6*r1)}return 0}function _Z(X,Q){if(X!=null){let Z=C1[X];if(Z==null)return null;return{text:Z,title:v1[X]}}if(Q)return{icon:{name:"file-tree-icon-dot",width:6,height:6},title:b1};return null}function FZ(X,Q,Z){if(Q==null||Q.size===0)return null;let Y=[];for(let J=X.length-1;J>=0;J-=1){let W=X[J],G=Z.get(W);if(G!=null){for(let q of Y)Z.set(q,G);return G?"ignored":null}if(Q.has(W)){Z.set(W,!0);for(let q of Y)Z.set(q,!0);return"ignored"}Y.push(W)}for(let J of Y)Z.set(J,!1);return null}function g8(X){return X!=null&&"toggle"in X}function G3(X){return X.code==="Space"||X.key===" "||X.key==="Spacebar"}function VZ(X){return X.key.length===1&&/^[\p{L}\p{N}]$/u.test(X.key)&&!X.ctrlKey&&!X.metaKey&&!X.altKey}function d6(X,Q){if(X==null)return Q;let Z=X.getBoundingClientRect().height;if(Z>0)return Z;return X.clientHeight>0?X.clientHeight:Q}function RZ(X,Q){return X!=null&&X>0?X:Q}function EZ(X){let Q=X.borderBoxSize,Z=Array.isArray(Q)?Q[0]:Q;if(Z!=null&&Number.isFinite(Z.blockSize)&&Z.blockSize>0)return Z.blockSize;return X.contentRect.height>0?X.contentRect.height:null}function DZ(X,Q,Z,Y,J=0){let W=y1({currentScrollTop:X.scrollTop,focusedIndex:Q,itemHeight:Z,topInset:J,viewportHeight:Y});if(W==null)return!1;return X.scrollTop=W,!0}function s6(X,Q,Z,Y,J,W){let G=x1({currentScrollTop:X.scrollTop,focusedIndex:Q,itemHeight:Z,targetViewportOffset:W,totalHeight:J,viewportHeight:Y});if(G==null)return!1;return X.scrollTop=G,!0}function t1(X,Q,Z,Y){if(Z.end<Z.start)return null;if(X<Z.start)return-Q;if(X>Z.end)return Y;return null}function kZ(X){if(X==null)return"";return`[data-item-section="spacing-item"][data-ancestor-path="${X.replaceAll("\\","\\\\").replaceAll('"',"\\\"")}"] { opacity: 1; }`}function q3(X){return X.shiftKey&&X.key==="F10"||X.key==="ContextMenu"}function TZ(X,Q){if(Q&&q3(X))return!0;if((X.ctrlKey||X.metaKey)&&G3(X))return!0;return X.key==="ArrowDown"||X.key==="ArrowLeft"||X.key==="ArrowRight"||X.key==="ArrowUp"}var wZ=new Set(["ArrowDown","ArrowLeft","ArrowRight","ArrowUp","End","Home","PageDown","PageUp"]);function e1(X){for(let Q of X.composedPath()){if(!(Q instanceof HTMLElement))continue;if(Q.dataset.fileTreeContextMenuRoot==="true")return!0;if(Q.dataset.type==="context-menu-anchor"||Q.dataset.type===q7)return!0;if(Q.getAttribute("slot")===k5)return!0}return!1}function NZ(X){return{bottom:X.bottom,height:X.height,left:X.left,right:X.right,top:X.top,width:X.width,x:X.x,y:X.y}}function CZ(X,Q){return{bottom:Q,height:0,left:X,right:X,top:Q,width:0,x:X,y:Q}}function vZ(X,Q){if(X==null)return Q.offsetTop;let Z=Q.getBoundingClientRect(),Y=X.getBoundingClientRect();return Z.top-Y.top}function X3(X,Q,Z){if(Z==null){X.delete(Q);return}X.set(Q,Z)}function Q3(X,Q,Z){if(X==null)return null;let Y=Q.get(X)??null;if(Y!=null)return Y;let J=Z.get(X)??null;return J?.dataset.itemParked==="true"?null:J}function bZ(X){if(X==null)return[];let Q=[];for(let Z of X.querySelectorAll('button[data-file-tree-sticky-row="true"]')){if(!(Z instanceof HTMLElement))continue;let Y=Z.dataset.fileTreeStickyPath;if(Y!=null)Q.push(Y)}return Q}function SZ(X,Q){if(X==null||Q==null)return null;for(let Z of X.querySelectorAll('button[data-item-focused="true"][data-item-parked="true"]'))if(Z instanceof HTMLElement&&Z.dataset.itemPath===Q)return Z;return null}function PZ(X,Q,Z,Y,J,W,G){let q=Math.max(0,W-J),U=Q?.getBoundingClientRect()??null,A=U==null||Z==null?null:Z.getBoundingClientRect().top-U.top,M=SZ(X,Y),O=U==null||M==null?null:M.getBoundingClientRect().top-U.top;return Math.max(0,Math.min(O??Math.max(A??0,q),Math.max(0,G-J)))}function Z3(X,Q){return{kind:X.kind,name:I8(X),path:Q}}function fZ(X){return X==null?void 0:`${X}__tree`}function $3(X,Q,Z){if(X==null)return;return`${X}__focused-item-${encodeURIComponent(Q)}${Z?"__parked":""}`}function Y3(X){return X==="file-tree-icon-chevron"||X==="file-tree-icon-dot"||X==="file-tree-icon-file"||X==="file-tree-icon-lock"}function J3(X,Q){if(X==null)return null;if("text"in X)return v("span",{title:X.title,children:X.text});let Z=typeof X.icon==="string"?Y3(X.icon)?Q(X.icon):{name:X.icon}:Y3(X.icon.name)?(()=>{let Y=Q(X.icon.name),{name:J,...W}=X.icon;return{...Y,...W}})():X.icon;return v("span",{title:X.title,children:v(L6,{...Z})})}function W3(X){if(X==null)return;j6(X.querySelector(["button:not([disabled])","[href]","input:not([disabled])","select:not([disabled])","textarea:not([disabled])",'[tabindex]:not([tabindex="-1"])'].join(", "))??X)}function yZ(X,Q,{actionLaneEnabled:Z=!1,customDecoration:Y=null,decorationLaneEnabled:J=!1,dragTargetFlattenedSegmentPath:W=null,gitDecoration:G=null,gitLaneActive:q=!1,renameInput:U=null,showDecorativeActionAffordance:A=!1}={}){let M=_6(X);return v($5,{children:[X.depth>0?v("div",{"data-item-section":"spacing",children:Array.from({length:X.depth}).map((O,z)=>v("div",{"data-item-section":"spacing-item","data-ancestor-path":X.ancestorPaths[z]},z))}):null,v("div",{"data-item-section":"icon",children:X.kind==="directory"?v(L6,{...Q("file-tree-icon-chevron")}):v(L6,{...Q("file-tree-icon-file",M)})}),v("div",{"data-item-section":"content",children:X.isFlattened?HZ(X,U,W):U??v(k1,{minimumLength:5,split:"extension",children:X.name})}),J?v("div",{"data-item-section":"decoration",children:Y!=null?J3(Y,Q):null}):null,q?v("div",{"data-item-section":"git",children:J3(G,Q)}):null,Z?v("div",{"data-item-section":"action",children:A?v("span",{"aria-hidden":"true","data-item-action-affordance":"decorative",children:v(L6,{...Q("file-tree-icon-ellipsis")})}):null}):null]})}function y7(X,Q,Z,Y={}){let{controller:J,renameView:W,visualFocusPath:G,contextHoverPath:q,draggedPathSet:U,dragTarget:A,dragAndDropEnabled:M,shouldSuppressContextMenu:O,handleRowDragStart:z,handleRowDragEnd:j,handleRowTouchStart:B,instanceId:R,itemHeight:D,gitStatusByPath:b,ignoredGitDirectories:w,ignoredInheritanceCache:F,directoriesWithGitChanges:V,gitLaneActive:k,contextMenuEnabled:P,contextMenuTriggerMode:h,contextMenuButtonTriggerEnabled:G4,contextMenuButtonVisibility:z4,contextMenuRightClickEnabled:d,registerRenameInput:Y4,registerButton:q4,resolveIcon:t,renderDecorationForRow:e,openContextMenuForRow:E4,onRowClick:W4,onKeyDown:B4}=X,$4=_6(Q),{isParked:N4=!1,mode:H="flow",style:T}=Y,x=H==="sticky",p=b?.get($4)??null??FZ(Q.ancestorPaths,w,F),j4=Q.kind==="directory"&&(V?.has($4)??!1),D4=e(Q,$4),c=_Z(p,j4),Z4=P&&G4,T4=D4!=null||k||Z4,b4=Z4&&z4==="always",L5=W.getPath()===$4,Q5=L5?W.getValue():"",P5=x||!L5?null:v(MZ,{ref:Y4,ariaLabel:`Rename ${I8(Q)}`,isFlattened:Q.isFlattened,value:Q5,onBlur:()=>{W.commit()},onInput:(X4)=>{W.setValue(X4.currentTarget.value)}}),c4=yZ(Q,t,{actionLaneEnabled:Z4,customDecoration:D4,decorationLaneEnabled:T4,dragTargetFlattenedSegmentPath:A?.flattenedSegmentPath??null,gitDecoration:c,gitLaneActive:k,renameInput:P5,showDecorativeActionAffordance:b4}),W5={...P1({ariaLabel:I8(Q),domId:Q.isFocused?$3(R,$4,N4):void 0,extraStyle:T,features:{actionLaneEnabled:Z4,contextMenuButtonVisibility:Z4?z4:null,contextMenuEnabled:P,contextMenuTriggerMode:P?h:null,gitLaneActive:k},isParked:N4,itemHeight:D,mode:H,row:Q,state:{containsGitChange:j4,effectiveGitStatus:p,isContextHovered:q===$4,isDragTarget:A?.kind==="directory"&&A.directoryPath===$4,isDragging:U?.has($4)===!0,isFocusRinged:Q.isFocused&&G===$4},targetPath:$4}),key:Z,onContextMenu:P||M?(X4)=>{if(O()){X4.preventDefault();return}if(!P)return;if(X4.preventDefault(),!d)return;J.focusPath($4),E4(Q,$4,{anchorRect:CZ(X4.clientX,X4.clientY),source:"right-click"})}:void 0,onFocus:!x?()=>{J.focusPath($4)}:void 0,onKeyDown:!x?B4:void 0,ref:(X4)=>{q4($4,X4)}};if(!x&&L5)return v("div",{...W5,children:c4});return v("button",{...W5,type:"button",draggable:M&&!N4,onDragEnd:M&&!N4?j:void 0,onDragStart:M&&!N4?(X4)=>{z(X4,Q,$4)}:void 0,onMouseDown:(X4)=>{if(x){X4.preventDefault();return}if(J.isSearchOpen())X4.preventDefault()},onTouchStart:M&&!N4?(X4)=>{B(X4,Q,$4)}:void 0,onClick:(X4)=>{W4(X4,Q,$4,H)},children:c4})}function xZ(X,Q,Z){if(Q.end<Q.start)return[];return X.controller.getVisibleRows(Q.start,Q.end).filter((Y)=>!Z.has(_6(Y))).map((Y,J)=>y7(X,Y,Q.start+J))}function m8({composition:X,controller:Q,gitStatusByPath:Z,ignoredGitDirectories:Y,directoriesWithGitChanges:J,icons:W,instanceId:G,itemHeight:q=U7,overscan:U=B9,renamingEnabled:A=!1,renderRowDecoration:M,searchBlurBehavior:O="close",searchEnabled:z=!1,searchFakeFocus:j=!1,slotHost:B,stickyFolders:R=!1,initialViewportHeight:D=z7}){let b=o(null),w=o(null),F=o(!1),V=o(null),k=o(null),P=o(null),h=o(null),G4=o(null),z4=o(new Map),d=o(new Map),Y4=o(()=>{}),q4=o(null),t=o(!1),e=o(null),E4=o(null),W4=o(!1),B4=o(null),$4=o(null),N4=o(null),H=o(null),T=o(null),x=o(null),p=o(null),j4=o(null),D4=o(!1),c=o(null),Z4=o(null),T4=o(null),b4=o(null),L5=A5(()=>new Map,[]),[,Q5]=J5(0),[P5,c4]=J5(null),[W5,X4]=J5(null),[r5,g7]=J5(null),[r,t4]=J5(null),[o6,r6]=J5(0),[K4,a5]=J5(null),f5=o(K4);f5.current=K4;let n5=o(null),O5=o(null),B5=o(null),j5=o(null),F6=o(null),U5=o(!1),t5=()=>{O5.current=null,B5.current=null,j5.current=null},_5=(K,_)=>{O5.current=K,B5.current=null,j5.current=_==null?null:{path:K,scrollTop:_}},V6=(K,_)=>{O5.current=null,B5.current={path:K,viewportOffset:_},j5.current=null},R6=o(O==="retain"&&Q.isSearchOpen()),[y5,$]=J5(j);f8(()=>{if(!j)$(!1)},[j]);let L=o(!1),E=I4(()=>{L.current=!0,$((K)=>K?!1:K)},[]),[N,m]=J5(()=>x8({controller:Q,itemHeight:q,overscan:U,scrollTop:0,stickyFolders:R,viewportHeight:D})),[a,s]=J5(!1);f8(()=>{s(!0)},[]);let i=X?.contextMenu?.enabled===!0||X?.contextMenu?.render!=null||X?.contextMenu?.onOpen!=null||X?.contextMenu?.onClose!=null,l=X?.contextMenu?.triggerMode??(i?"right-click":"both"),m4=l==="both"||l==="button",z5=X?.contextMenu?.buttonVisibility??"when-needed",I7=l==="both"||l==="right-click";i4(()=>{let K=P.current;if(K==null)return;let _=(C)=>{if(!(C instanceof CustomEvent))return;let f=C.detail?.path??null;F6.current=f,X4(f),t4(f==null?null:"pointer")},g=(C)=>{if(!(C instanceof CustomEvent))return;U5.current=C.detail?.disabled===!0};return K.addEventListener("file-tree-debug-set-context-menu-trigger",_),K.addEventListener("file-tree-debug-set-scroll-suppression",g),()=>{K.removeEventListener("file-tree-debug-set-context-menu-trigger",_),K.removeEventListener("file-tree-debug-set-scroll-suppression",g)}},[]);let m7=I4((K,_)=>{X3(z4.current,K,_)},[]),F3=I4((K,_)=>{X3(d.current,K,_)},[]),V3=I4((K)=>{k.current=K},[]),E6=I4((K)=>{return Q3(K,d.current,z4.current)},[]),h8=Z!=null||Y!=null||J!=null,{resolveIcon:p8}=A5(()=>q1(W),[W]),D6=Q[B8](),e5=D6.getPath(),u7=e5!=null,F5=Q.isSearchOpen(),R3=Q.getSearchValue(),Q4=Q.getFocusedPath(),L4=Q.getFocusedIndex(),K5=Q.isDragAndDropEnabled(),k6=Q.getDragSession(),E3=A5(()=>k6==null?null:new Set(k6.draggedPaths),[k6]),D3=k6?.target??null,T6=k6?.primaryPath??null,c8=fZ(G),{overlayHeight:k3,overlayRows:T3,snapshot:S4,visibleRows:a6}=N,l4=S4.physical.viewportHeight,Z5=A5(()=>({end:S4.window.endIndex,start:S4.window.startIndex}),[S4.window.endIndex,S4.window.startIndex]),w6=T3,l8=S4.sticky.rows,X6=S4.physical.totalHeight,N6=S4.sticky.height,n6=A5(()=>new Set(l8.map((K)=>_6(K.row))),[l8]),h7=L4>=0&&L4>=Z5.start&&L4<=Z5.end,w3=I4((K,_)=>M?.({item:Z3(K,_),row:K})??null,[M]),d8=I4((K)=>{if(j6(K==null?null:z4.current.get(K)??null))return!0;return j6(P.current)},[]),t6=I4((K)=>{d8(Q.focusNearestPath(K))},[Q,d8]),s8=o(t6);s8.current=t6;let Q6=o(!0),p7=o(()=>{}),e4=I4((K=!0)=>{let _=f5.current;if(_==null)return;if(Q6.current=Q6.current&&K,a5(null),X?.contextMenu?.onClose?.(),Q6.current)t6(_.path)},[X?.contextMenu,t6]);p7.current=e4;let C6=I4((K)=>{let _=K==null?null:vZ(P.current,K);g7((g)=>g===_?g:_)},[]),i8=I4((K,_,g)=>{let C=Q.getItem(_);if(C==null)return;let f=E6(_);if(f?.dataset.fileTreeStickyRow==="true"){let u=h.current;_5(_,u?.scrollTop??null),t.current=!0,c4((F4)=>F4===_?F4:_)}C.focus(),C6(f),Q6.current=!0,a5({anchorRect:g?.anchorRect??null,item:Z3(K,_),path:_,source:g?.source??"keyboard"})},[Q,E6,C6]),N3=I4((K)=>{if(!A)return;if(Q.isSearchOpen()){let _=h.current,g=d6(_,l4);B4.current=L4<0||_==null?null:Math.max(0,Math.min(L4*q-_.scrollTop,Math.max(0,g-q))),W4.current=!0}if(Q.startRenaming(K)===!1)return;t4("focus"),Q5((_)=>_+1)},[Q,L4,q,A,l4]),e6=I4((K,{restoreTreeFocus:_=!0,targetOffset:g="live-overlay"}={})=>{let C=h.current;if(C==null)return!1;Q.focusPath(K);let f=Q.getFocusedIndex();if(f<0)return!1;let u=Q.getVisibleRows(f,f)[0]??null;if(u==null)return!1;let F4=d6(C,l4),n=Q.getVisibleCount()*q,J4=g==="sticky-parents"?u.ancestorPaths.length*q:x8({controller:Q,itemHeight:q,overscan:U,scrollTop:C.scrollTop,stickyFolders:R,viewportHeight:F4}).snapshot.sticky.height;return t.current=!0,s6(C,f,q,F4,n,J4),Y4.current(),n5.current=_?K:null,!0},[Q,q,U,l4,R]),C3=()=>{return F.current===!0||b4.current!=null||D4.current===!0},o8=(K)=>{return typeof window.requestAnimationFrame==="function"?window.requestAnimationFrame(()=>{K()}):window.setTimeout(K,16)},v3=(K)=>{if(K==null)return;if(typeof window.cancelAnimationFrame==="function"){window.cancelAnimationFrame(K);return}window.clearTimeout(K)},V5=()=>{if(H.current!=null)clearTimeout(H.current),H.current=null;N4.current=null},X7=()=>{x.current?.remove(),x.current=null},v6=()=>{v3($4.current),$4.current=null,T.current=null},r8=(K)=>{let _=P.current?.getRootNode();if(_ instanceof ShadowRoot){_.append(K);return}document.body.append(K)},b6=()=>{if(j4.current?.(),j4.current=null,b4.current!=null)clearTimeout(b4.current),b4.current=null;if(D4.current=!1,c.current=null,T4.current=null,Z4.current!=null)Z4.current.setAttribute("draggable","true"),Z4.current.style.removeProperty("touch-action"),Z4.current=null;X7(),V5(),v6(),p.current=null},Q7=(K,_)=>{let g=P.current?.getRootNode(),C=a1(LZ(g instanceof ShadowRoot?g:document,K,_));return Q.setDragTarget(C),Q.getDragSession()?.target??null},c7=(K)=>{let _=Q.getDragAndDropConfig()?.openOnDropDelay??800;if(K==null||K.kind!=="directory"||K.directoryPath==null||_<=0){V5();return}let g=Q.getItem(K.directoryPath),C=g8(g)?g:null;if(C==null||C.isExpanded()){V5();return}let f=`${K.directoryPath}::${K.flattenedSegmentPath??""}`;if(N4.current===f)return;V5(),N4.current=f,H.current=setTimeout(()=>{let u=Q.getDragSession()?.target;if(u?.kind!=="directory"||u.directoryPath!==K.directoryPath||u.flattenedSegmentPath!==K.flattenedSegmentPath)return;C.expand()},_)},a8=()=>{$4.current=null;let K=T.current,_=h.current;if(K==null||_==null||Q.getDragSession()==null)return;let g=_.getBoundingClientRect(),C=jZ(K.clientY,g);if(C===0)return;let f=Math.max(0,_.scrollHeight-_.clientHeight),u=Math.max(0,Math.min(f,_.scrollTop+C));if(u!==_.scrollTop)_.scrollTop=u,Y4.current();c7(Q7(K.clientX,K.clientY)),$4.current=o8(a8)},n8=(K,_)=>{T.current={clientX:K,clientY:_},$4.current??=o8(a8)},b3=(K,_,g)=>{let C=K.currentTarget;if(C==null)return;if(b6(),X7(),V5(),v6(),Q.startDrag(g)===!1){K.preventDefault();return}if(p.current=_,K.dataTransfer!=null){if(K.dataTransfer.effectAllowed="move",K.dataTransfer.dropEffect="move",K.dataTransfer.setData("text/plain",g),BZ()){let f=n1(C),u=C.getBoundingClientRect();Object.assign(f.style,{height:`${u.height}px`,opacity:"0.85",transform:"translate3d(-9999px, 0px, 0)",width:`${u.width}px`}),r8(f),x.current=f,K.dataTransfer.setDragImage(f,Math.max(0,K.clientX-u.left),Math.max(0,K.clientY-u.top))}}},S3=()=>{X7(),V5(),v6(),p.current=null,Q.cancelDrag()},P3=(K,_,g)=>{if(b4.current!=null||D4.current)return;let C=K.touches[0],f=K.currentTarget;if(C==null||f==null)return;T4.current={clientX:C.clientX,clientY:C.clientY},Z4.current=f,f.setAttribute("draggable","false");let u=(J4={})=>{let H4=J4.restoreNativeDraggable??!D4.current;if(b4.current!=null)clearTimeout(b4.current),b4.current=null;if(document.removeEventListener("touchmove",F4),document.removeEventListener("touchend",n),document.removeEventListener("touchcancel",n),j4.current===u)j4.current=null;if(H4){if(f.setAttribute("draggable","true"),Z4.current===f)Z4.current=null;T4.current=null}},F4=(J4)=>{let H4=J4.touches[0],V4=T4.current;if(H4==null||V4==null)return;let P4=H4.clientX-V4.clientX,C4=H4.clientY-V4.clientY;if(P4*P4+C4*C4<=o1*o1)return;u()},n=()=>{u()};document.addEventListener("touchmove",F4,{passive:!0}),document.addEventListener("touchend",n),document.addEventListener("touchcancel",n),j4.current=u,b4.current=setTimeout(()=>{if(u({restoreNativeDraggable:!1}),Q.startDrag(g)===!1){if(f.setAttribute("draggable","true"),Z4.current===f)Z4.current=null;T4.current=null;return}D4.current=!0,Z4.current=f,f.setAttribute("draggable","false"),f.style.setProperty("touch-action","none"),p.current=_;let J4=f.getBoundingClientRect(),H4=n1(f);Object.assign(H4.style,{height:`${J4.height}px`,opacity:"0.85",transform:`translate3d(${J4.left}px, ${J4.top}px, 0)`,width:`${J4.width}px`}),r8(H4),x.current=H4,c.current={x:C.clientX-J4.left,y:C.clientY-J4.top};let V4=(G5)=>{let v4=G5.touches[0];if(v4==null)return;G5.preventDefault();let o4=c.current;if(o4!=null&&x.current!=null)x.current.style.transform=`translate3d(${v4.clientX-o4.x}px, ${v4.clientY-o4.y}px, 0)`;c7(Q7(v4.clientX,v4.clientY)),n8(v4.clientX,v4.clientY)},P4=(G5)=>{let v4=G5.changedTouches[0];if(v4!=null)Q7(v4.clientX,v4.clientY);Q.completeDrag(),b6()},C4=()=>{Q.cancelDrag(),b6()};j4.current=()=>{document.removeEventListener("touchmove",V4),document.removeEventListener("touchend",P4),document.removeEventListener("touchcancel",C4)},document.addEventListener("touchmove",V4,{passive:!1}),document.addEventListener("touchend",P4),document.addEventListener("touchcancel",C4)},AZ)},t8=(K)=>{if(K4!=null){if(K.key==="Escape"){e4(),K.preventDefault(),K.stopPropagation();return}if(wZ.has(K.key))K.preventDefault(),K.stopPropagation();return}if(D6.isActive()){if(K.key==="Escape")D6.cancel();else if(K.key==="Enter")D6.commit();else return;t4("focus"),Q5((R4)=>R4+1),K.preventDefault(),K.stopPropagation();return}if(A&&K.key==="F2"){N3(Q4??void 0),K.preventDefault(),K.stopPropagation();return}if(F5){if(K.key==="Escape")W4.current=!1,B4.current=null,Q.closeSearch();else if(K.key==="Enter"){let R4=Q.getFocusedPath();if(R4!=null)Q.selectOnlyPath(R4);let E5=h.current,YX=d6(E5,l4);B4.current=L4<0||E5==null?null:Math.max(0,Math.min(L4*q-E5.scrollTop,Math.max(0,YX-q))),W4.current=!0,Q.closeSearch()}else if(K.key==="ArrowDown")Q.focusNextSearchMatch();else if(K.key==="ArrowUp")Q.focusPreviousSearchMatch();else return;t4("focus"),Q5((R4)=>R4+1),K.preventDefault(),K.stopPropagation();return}if(z&&VZ(K)){Q.openSearch(K.key),Q5((R4)=>R4+1),K.preventDefault(),K.stopPropagation();return}let _=i&&q3(K),g=TZ(K,i),C=g&&P.current!=null?f7(P.current):null,f=g?new Set(bZ(P.current)):new Set,u=C?.dataset.fileTreeStickyPath??null,F4=C?.dataset.fileTreeStickyRow==="true"&&u!=null;if(F4&&u!==Q4&&f.has(u)){let R4=h.current;_5(u,R4?.scrollTop??null),Q.focusPath(u)}let n=Q.getFocusedPath(),J4=Q.getFocusedIndex(),H4=Q.getFocusedItem();if(H4==null)return;let V4=g8(H4)?H4:null,P4=n!=null&&(n6.has(n)||F4&&u===n&&f.has(n)),C4=K.key==="ArrowDown"||K.key==="ArrowUp"||K.key==="ArrowRight"&&V4!=null&&V4.isExpanded(),G5=K.key==="ArrowLeft"&&P4&&V4!=null&&V4.isExpanded(),v4=h.current,o4=!0;if(K.shiftKey&&K.key==="ArrowDown")Q.extendSelectionFromFocused(1);else if(K.shiftKey&&K.key==="ArrowUp")Q.extendSelectionFromFocused(-1);else if(_&&n!=null&&J4>=0){let R4=Q.getVisibleRows(J4,J4)[0]??null,E5=Q3(n,d.current,z4.current);if(R4==null||E5==null)o4=!1;else i8(R4,n)}else if((K.ctrlKey||K.metaKey)&&G3(K))Q.toggleFocusedSelection();else if((K.ctrlKey||K.metaKey)&&K.key.toLowerCase()==="a")Q.selectAllVisiblePaths();else switch(K.key){case"ArrowDown":Q.focusNextItem();break;case"ArrowUp":Q.focusPreviousItem();break;case"ArrowRight":if(V4==null||V4.isExpanded())Q.focusNextItem();else V4.expand();break;case"ArrowLeft":if(V4!=null&&V4.isExpanded())V4.collapse();else Q.focusParentItem();break;case"Home":Q.focusFirstItem();break;case"End":Q.focusLastItem();break;default:o4=!1}if(!o4)return;t4("focus");let U4=Q.getFocusedPath(),Y6=U4!=null&&(n6.has(U4)||f.has(U4)),g5=C4&&U4!==n,W7=_&&F4&&u===n&&U4===n;if((P4||W7)&&U4!=null&&(g5&&Y6||W7))_5(U4,v4?.scrollTop??null),t.current=!0,c4((R4)=>R4===U4?R4:U4);else{let R4=K.key==="ArrowUp"&&P4&&U4!==n;if(U4!=null&&(R4||G5&&U4===n))V6(U4,PZ(P.current,v4,C,n,q,N6,l4)),t.current=!0,c4((E5)=>E5===U4?E5:U4);else t5()}Q5((R4)=>R4+1),K.preventDefault(),K.stopPropagation()};i4(()=>{if(!z||!F5)return;if(R6.current){R6.current=!1;return}j6(G4.current)},[F5,z]),i4(()=>{let K=k.current;switch(S1({hasRenderedInput:K!=null,previousRenamingPath:E4.current,renamingPath:e5})){case"reset":E4.current=null;return;case"reveal-canonical":if(e5!=null)e6(e5,{restoreTreeFocus:!1,targetOffset:"live-overlay"});return;case"ignore":return;case"focus-input":if(K!=null)n5.current=null,E4.current=e5,j6(K),K.select();return}},[Z5.end,Z5.start,e5,e6,n6]),i4(()=>{let K=P.current;if(K==null)return;let _=null,g=()=>{if(_==null)return;clearTimeout(_),_=null},C=()=>{let F4=f7(K)?.dataset.itemPath??null;c4((n)=>n===F4?n:F4)},f=()=>{g(),t.current=!0,C()},u=(F4)=>{let n=F4.relatedTarget;if(n==null){g(),_=setTimeout(()=>{if(_=null,f7(K)!=null){C();return}t.current=!1,c4(null)},0);return}if(!(n instanceof Node)||!K.contains(n)){g(),t.current=!1,c4(null);return}let J4=n instanceof HTMLElement?n.dataset.itemPath??null:null;c4((H4)=>H4===J4?H4:J4)};return K.addEventListener("focusin",f),K.addEventListener("focusout",u),()=>{g(),K.removeEventListener("focusin",f),K.removeEventListener("focusout",u)}},[]),i4(()=>{let K=P.current;if(K==null)return;if(S4.physical.scrollTop<=0)K.dataset.scrollAtTop="true";else delete K.dataset.scrollAtTop},[S4.physical.scrollTop]),i4(()=>{let K=null,_=h.current,g=V.current,C=P.current;if(_==null)return;q4.current=d6(_,D);let f=()=>{let U4=Q.getVisibleCount(),Y6=RZ(q4.current,D),g5=Math.max(0,U4*q-Y6);if(_.scrollTop>g5)_.scrollTop=g5;m(x8({controller:Q,itemHeight:q,overscan:U,scrollTop:Math.min(_.scrollTop,g5),stickyFolders:R,viewportHeight:Y6}))};Y4.current=f;let u=!1,F4=Q.subscribe(()=>{if(u)Q5((U4)=>U4+1);else u=!0;f()}),n=()=>{if(U5.current===!0)return;if(g!=null)g.dataset.isScrolling??="";if(C!=null)C.dataset.isScrolling??="";if(F.current=!0,K!=null)clearTimeout(K);K=setTimeout(()=>{if(g!=null)delete g.dataset.isScrolling;if(C!=null)delete C.dataset.isScrolling;F.current=!1,r6((U4)=>U4+1),K=null},50)},J4=null,H4=()=>{if(C!=null)delete C.dataset.overlayReveal;if(J4!=null)clearTimeout(J4),J4=null},V4=()=>{if(C==null||U5.current===!0)return;if(_.scrollTop>0)return;if(C.dataset.overlayReveal="true",J4!=null)clearTimeout(J4);J4=setTimeout(()=>{H4()},200)},P4=()=>{if(f(),_.scrollTop>0)H4();if(f5.current!=null&&F.current)p7.current();if(U5.current===!0){F.current=!1;return}X4((U4)=>U4==null?U4:null),n()},C4=()=>{n(),V4()},G5=new Set(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","PageUp","PageDown","Home","End"," ","Spacebar"]),v4=(U4)=>{if(!G5.has(U4.key))return;C4()};_.addEventListener("scroll",P4,{passive:!0}),_.addEventListener("wheel",C4,{passive:!0}),_.addEventListener("touchmove",C4,{passive:!0}),_.addEventListener("keydown",v4);let o4=typeof ResizeObserver<"u"?new ResizeObserver((U4)=>{q4.current=(U4[0]==null?null:EZ(U4[0]))??d6(_,D),f()}):null;return o4?.observe(_),()=>{if(Y4.current=()=>{},F4(),_.removeEventListener("scroll",P4),_.removeEventListener("wheel",C4),_.removeEventListener("touchmove",C4),_.removeEventListener("keydown",v4),K!=null)clearTimeout(K);if(J4!=null)clearTimeout(J4);if(g!=null)delete g.dataset.isScrolling;if(C!=null)delete C.dataset.isScrolling,delete C.dataset.overlayReveal;F.current=!1,q4.current=null,o4?.disconnect()}},[Q,D,q,U,R]),i4(()=>{if(i||K4==null)return;e4(!1)},[e4,i,K4]);let e8=A5(()=>K4==null?null:`${K4.path}::${K4.source}`,[K4]);i4(()=>{if(e8==null){B?.clearSlotContent(k5);return}let K=f5.current;if(K==null)return;let _=w.current??b.current;if(_==null)return;let g={anchorElement:_,anchorRect:K.anchorRect??NZ(_.getBoundingClientRect()),close:(f)=>{p7.current(f?.restoreFocus??!0)},restoreFocus:()=>{if(!Q6.current)return;s8.current(f5.current?.path??null)}},C=X?.contextMenu?.render?.(K.item,g)??null;return B?.setSlotContent(k5,C),X?.contextMenu?.onOpen?.(K.item,g),W3(C),queueMicrotask(()=>{if(C==null||!C.isConnected)return;if(document.activeElement!==C)return;W3(C)}),()=>{B?.clearSlotContent(k5)}},[e8,X?.contextMenu,B]),i4(()=>{if(K4!=null&&Q.getItem(K4.path)==null)e4()},[e4,K4,Q]),i4(()=>{if(K4==null)return;let K=P.current?.getRootNode(),_=K instanceof ShadowRoot?K.host:P.current,g=(f)=>{let u=f.target;if(!(u instanceof Node))return;if(e1(f))return;if(b.current?.contains(u)===!0)return;if(_?.contains(u)===!0)return;e4()},C=(f)=>{if(f.key==="Escape")f.preventDefault(),f.stopPropagation(),e4()};return document.addEventListener("mousedown",g,!0),document.addEventListener("keydown",C,!0),()=>{document.removeEventListener("mousedown",g,!0),document.removeEventListener("keydown",C,!0)}},[e4,K4]),i4(()=>{let K=h.current,_=P.current;if(K==null||_==null){e.current=Q4;return}let g=Q4==null?null:z4.current.get(Q4)??null,C=f7(_),f=C?.dataset.itemPath??null,u=u7&&k.current===C,F4=z&&G4.current===C,n=W4.current&&!F5,J4=B4.current??0,H4=n5.current,V4=O5.current,P4=B5.current,C4=j5.current,G5=C!=null,v4=t.current||G5,o4=e.current!==Q4,U4=V4!=null&&V4===Q4&&Q4!=null,Y6=n&&s6(K,L4,q,l4,X6,J4),g5=H4!=null&&H4===Q4&&s6(K,L4,q,l4,X6,N6),W7=P4!=null&&P4.path===Q4&&s6(K,L4,q,l4,X6,P4.viewportOffset),R4=C4!=null&&C4.path===Q4&&K.scrollTop!==C4.scrollTop;if(R4)K.scrollTop=C4.scrollTop;if(R4||g5||W7||Y6||v4&&o4&&H4!==Q4&&!U4&&DZ(K,L4,q,l4,N6))Y4.current();if(!v4){e.current=Q4;return}if(u){e.current=Q4;return}if(F4&&!n){e.current=Q4;return}if(g==null){if(n&&L4>=0)s6(K,L4,q,l4,X6,J4),Y4.current();e.current=Q4;return}if(o4||n||H4===Q4||V4===Q4||P4?.path===Q4||C4?.path===Q4||f==null||f!==Q4){if(j6(g),H4===Q4)n5.current=null;if(V4===Q4)O5.current=null;if(P4?.path===Q4)B5.current=null;if(C4?.path===Q4)j5.current=null;W4.current=!1,B4.current=null}e.current=Q4},[Q,L4,Q4,h7,q,u7,F5,Z5,l4,z,N6,X6,a6]);let f3=L4>=0&&L4>=S4.visible.startIndex&&L4<=S4.visible.endIndex,y3=Q4!=null&&w6.some((K)=>_6(K.row)===Q4),x3=f3||y3,g3=m4&&t.current===!0&&x3?Q4:null,I3=r==="pointer"?W5:null,x5=K4?.path??F6.current??I3??g3??W5,X9=K4?.source==="right-click";i4(()=>{if(F.current&&K4==null)return;C6(E6(x5))},[K4,E6,Z5,l4,o6,w6,x5,C6,a6]);let m3=I4((K)=>{if(F.current)return;if(e1(K))return;let _=K.target;if(!(_ instanceof HTMLElement))return;if(_.closest?.(`[data-type="${q7}"]`)!=null)return;let g=_.closest?.('[data-file-tree-sticky-row="true"]'),C=_.closest?.('[data-type="item"]'),f=g instanceof HTMLElement?g.dataset.fileTreeStickyPath??null:C instanceof HTMLElement?C.dataset.itemPath??null:null;if(f!=null)t4((u)=>u==="pointer"?u:"pointer");X4((u)=>u===f?u:f)},[]),u3=I4(()=>{X4(null)},[]);i4(()=>{if(!K5)return;let K=()=>{b6(),Q.cancelDrag()};return window.addEventListener("dragend",K),()=>{window.removeEventListener("dragend",K),b6(),Q.cancelDrag()}},[Q,K5]);let h3=(K)=>{if(!K5||Q.getDragSession()==null||D4.current)return;let _=a1(K.target instanceof HTMLElement?K.target:null);if(Q.setDragTarget(_),c7(Q.getDragSession()?.target??null),n8(K.clientX,K.clientY),K.dataTransfer!=null)K.dataTransfer.dropEffect="move";K.preventDefault()},p3=(K)=>{if(!K5||Q.getDragSession()==null||D4.current)return;let _=K.relatedTarget;if(_ instanceof Node&&P.current?.contains(_)===!0)return;V5(),v6(),Q.setDragTarget(null)},c3=(K)=>{if(!K5||Q.getDragSession()==null||D4.current)return;K.preventDefault(),Q7(K.clientX,K.clientY),Q.completeDrag(),X7(),V5(),v6(),p.current=null},Z7=S4.window.height,l3=S4.window.offsetTop,Q9=Math.min(0,l4-Z7-N6),d3=P5===Q4||W4.current,Z6=Q4!=null&&d3&&!h7&&L4>=0?a6[L4]??Q.getVisibleRows(L4,L4)[0]??null:null,Z9=Z6==null?null:t1(L4,q,Z5,Z7),R5=p.current,s3=T6!=null&&R5!=null&&R5.path===T6&&R5.index>=Z5.start&&R5.index<=Z5.end,S6=T6!=null&&R5!=null&&R5.path===T6&&!s3&&R5.path!==Z6?.path?R5:null,Y9=S6==null?null:t1(S6.index,q,Z5,Z7),i3=kZ((L4>=0?a6[L4]??Q.getVisibleRows(L4,L4)[0]??null:null)?.ancestorPaths.at(-1)??null),o3=F5&&Q4!=null?$3(G,Q4,!h7):void 0,r3=K4?.path??(F5?Q4:P5),a3=K4?.path??W5,P6=E6(x5),l7=i&&m4&&!X9&&!u7&&P6!=null&&r5!=null&&x5!=null,n3=i&&(l7||K4!=null),Y7=K4?.anchorRect,J9=Y7==null&&P6!=null&&r5!=null&&(K4!=null||l7)?r5:null,t3=Y7!=null?{left:`${Y7.left}px`,position:"fixed",right:"auto",top:`${Y7.top}px`}:J9!=null?{top:`${J9}px`}:void 0,e3=X9?{opacity:"0"}:void 0,XX=I4((K,_,g,C)=>{let f=Q.getItem(g),u=f1({event:{ctrlKey:K.ctrlKey,metaKey:K.metaKey,shiftKey:K.shiftKey},isDirectory:_.kind==="directory",isSearchOpen:Q.isSearchOpen(),mode:C});switch(u.selection.kind){case"range":Q.selectPathRange(g,u.selection.additive);break;case"toggle":Q.togglePathSelectionFromInput(g);break;case"single":Q.selectOnlyPath(g);break}let F4=K.currentTarget instanceof HTMLElement?K.currentTarget:null,n=_.index>=S4.visible.startIndex&&_.index<=S4.visible.endIndex,J4=C==="flow"&&n&&F4!=null&&F4.dataset.itemParked!=="true";if(f?.focus(),J4)t.current=!0,c4((H4)=>H4===g?H4:g),t4("focus");if(u.toggleDirectory&&g8(f))f.toggle();if(u.closeSearch)Q.closeSearch();if(u.revealCanonical)e6(g,{targetOffset:"sticky-parents"})},[Q,S4.visible.endIndex,S4.visible.startIndex,e6]),QX=()=>{if(F.current)return;if(!m4)return;if(x5==null||P6==null)return;let K=Q.getItem(x5);if(K==null)return;C6(P6),Q6.current=!0,a5({anchorRect:null,item:{kind:K.isDirectory()?"directory":"file",name:P6.getAttribute("aria-label")??x5,path:K.getPath()},path:K.getPath(),source:"button"})},J7={contextHoverPath:a3,contextMenuButtonTriggerEnabled:m4,contextMenuButtonVisibility:z5,contextMenuEnabled:i,contextMenuRightClickEnabled:I7,contextMenuTriggerMode:l,controller:Q,directoriesWithGitChanges:J,dragAndDropEnabled:K5,draggedPathSet:E3,dragTarget:D3,gitLaneActive:h8,gitStatusByPath:Z,handleRowDragEnd:S3,handleRowDragStart:b3,handleRowTouchStart:P3,ignoredGitDirectories:Y,ignoredInheritanceCache:L5,instanceId:G,itemHeight:q,onKeyDown:t8,onRowClick:XX,openContextMenuForRow:i8,registerButton:m7,registerRenameInput:V3,renameView:D6,renderDecorationForRow:w3,resolveIcon:p8,shouldSuppressContextMenu:C3,visualFocusPath:r3},ZX={...J7,registerButton:F3};return v("div",{ref:P,id:c8,"data-file-tree-context-menu-button-visibility":i&&m4?z5:void 0,"data-file-tree-context-menu-trigger-mode":i?l:void 0,"data-file-tree-has-context-menu-action-lane":i&&m4?"true":void 0,"data-file-tree-has-git-lane":h8?"true":void 0,"data-file-tree-virtualized-root":"true",onDragLeave:K5?p3:void 0,onDragOver:K5?h3:void 0,onDrop:K5?c3:void 0,onKeyDown:t8,onPointerLeave:i?u3:void 0,onPointerOver:i?m3:void 0,role:"tree",tabIndex:-1,style:{outline:"none",position:"relative"},children:[v("style",{"data-file-tree-guide-style":"true",dangerouslySetInnerHTML:{__html:i3}}),v("slot",{name:m5,"data-type":"header-slot"}),z?v("div",{"data-file-tree-search-container":!0,"data-open":F5?"true":"false",children:v("input",{ref:G4,"aria-activedescendant":o3,"aria-controls":c8,placeholder:"Search…","data-file-tree-search-input":!0,"data-file-tree-search-input-fake-focus":y5?"true":void 0,value:R3,onBlur:()=>{if(O==="retain"&&!L.current)return;Q.closeSearch()},onFocus:E,onPointerDown:E,onInput:(K)=>{E();let _=K.currentTarget;Q.setSearch(_.value)}})}):null,v("div",{ref:h,"data-file-tree-virtualized-scroll":"true",children:[R&&a&&w6.length>0?v("div",{"aria-hidden":"true","data-file-tree-sticky-overlay":"true",children:v("div",{"data-file-tree-sticky-overlay-content":"true",style:{height:`${k3}px`},children:w6.map((K,_)=>y7(ZX,K.row,`sticky:${_6(K.row)}`,{mode:"sticky",style:{left:"0",position:"absolute",right:"0",top:`${K.top}px`,zIndex:`${w6.length-_}`}}))})}):null,v("div",{ref:V,"data-file-tree-virtualized-list":"true",style:{height:`${X6}px`},children:[v("div",{"data-file-tree-virtualized-sticky-offset":"true","aria-hidden":"true",style:{height:`${l3}px`}}),v("div",{"data-file-tree-virtualized-sticky":"true",style:{height:`${Z7}px`,top:`${Q9}px`,bottom:`${Q9}px`},children:[xZ(J7,Z5,n6),Z6!=null&&Z9!=null?y7(J7,Z6,`parked:${Z6.path}`,{isParked:!0,style:{left:"0",opacity:"0",pointerEvents:T6===Z6.path?"none":void 0,position:"absolute",right:"0",top:`${Z9}px`}}):null,S6!=null&&Y9!=null?y7(J7,S6,`parked-drag:${S6.path}`,{isParked:!0,style:{left:"0",opacity:"0",pointerEvents:"none",position:"absolute",right:"0",top:`${Y9}px`}}):null]})]})]}),i?v("div",{ref:b,"data-type":"context-menu-anchor","data-visible":n3?"true":"false",style:t3,children:[v("button",{ref:w,type:"button","data-type":q7,"aria-label":"Options","aria-haspopup":"menu","aria-expanded":K4!=null?"true":"false","data-visible":l7?"true":"false",onMouseDown:(K)=>{K.preventDefault()},onClick:(K)=>{if(K.preventDefault(),K.stopPropagation(),K4!=null){e4();return}QX()},tabIndex:-1,style:e3,children:v(L6,{...p8("file-tree-icon-ellipsis")})}),K4!=null?v("slot",{name:k5}):null]}):null,K4!=null?v("div",{"data-type":"context-menu-wash","aria-hidden":"true",onMouseDownCapture:(K)=>{K.preventDefault(),e4()},onTouchStartCapture:(K)=>{K.preventDefault(),K.stopPropagation(),e4()},onTouchMoveCapture:(K)=>{K.preventDefault(),K.stopPropagation()},onWheelCapture:(K)=>{K.preventDefault(),K.stopPropagation()}}):null]})}var u8={hydrateRoot:(X,Q)=>{R1(A6(m8,Q),X)},renderRoot:(X,Q)=>{b7(A6(m8,Q),X)},unmountRoot:(X)=>{b7(null,X)}};function i6(X,Q){u8.renderRoot(X,Q)}function U3(X,Q){u8.hydrateRoot(X,Q)}function z3(X){u8.unmountRoot(X)}var K3=class{#X=new Map;#Z=null;clearAll(){for(let X of this.#X.values())X.remove();this.#X.clear()}clearSlotContent(X){let Q=this.#U(X);if(Q==null)return;Q.remove(),this.#X.delete(X)}setHost(X){if(this.#Z=X,X==null)return;this.#G(X);for(let[Q,Z]of this.#X)this.#z(Q,Z)}setSlotContent(X,Q){let Z=this.#U(X);if(Z===Q){if(Q!=null)this.#X.set(X,Q),this.#z(X,Q);return}if(Z?.remove(),Q==null){this.#X.delete(X);return}this.#X.set(X,Q),this.#z(X,Q)}setSlotHtml(X,Q){let Z=Q?.trim()??"";if(Z.length===0){this.setSlotContent(X,null);return}let Y=this.#U(X);if(Y!=null&&Y.innerHTML===Z){this.#X.set(X,Y),this.#z(X,Y);return}let J=document.createElement("div");J.innerHTML=Z,this.setSlotContent(X,J)}#U(X){let Q=this.#X.get(X)??null;if(Q!=null)return Q;let Z=this.#Z;if(Z==null)return null;for(let Y of Array.from(Z.children)){if(!(Y instanceof HTMLElement))continue;if(Y.dataset.fileTreeManagedSlot===X)return Y}return null}#z(X,Q){if(Q.slot=X,Q.dataset.fileTreeManagedSlot=X,this.#Z!=null&&Q.parentNode!==this.#Z)this.#Z.appendChild(Q)}#G(X){for(let Q of Array.from(X.children)){if(!(Q instanceof HTMLElement))continue;let Z=Q.dataset.fileTreeManagedSlot;if(Z==null||this.#X.has(Z))continue;this.#X.set(Z,Q)}}};var M3=0;function gZ(X){if(X!=null&&X.length>0)return X;return M3+=1,`pst_ft_${M3}`}function IZ({initialVisibleRowCount:X,itemHeight:Q}){return X==null?z7:Math.max(0,X)*(Q??U7)}function H3(X){if(typeof document>"u")return;let Q=document.createElement("div");Q.innerHTML=X;let Z=Q.querySelector("svg");return Z instanceof SVGElement?Z:void 0}function A3(X){return X.querySelector("#file-tree-icon-chevron")instanceof SVGElement&&X.querySelector("#file-tree-icon-file")instanceof SVGElement&&X.querySelector("#file-tree-icon-dot")instanceof SVGElement&&X.querySelector("#file-tree-icon-lock")instanceof SVGElement}function L3(X){return Array.from(X.children).filter((Q)=>Q instanceof SVGElement)}var O3=class{static LoadedCustomComponent=V9;#X;#Z;#U;#z;#G;#x;#g;#O;#Y;#B=new K3;#w;#j;#H;#_;#F;#V;#M;#I;#m;#P=null;#J;#u=!1;#h=!1;constructor(X){let{composition:Q,density:Z,fileTreeSearchMode:Y,gitStatus:J,id:W,initialSearchQuery:G,icons:q,itemHeight:U,onSearchChange:A,onSelectionChange:M,overscan:O,renderRowDecoration:z,renaming:j,search:B,searchBlurBehavior:R,searchFakeFocus:D,stickyFolders:b,unsafeCSS:w,initialVisibleRowCount:F,...V}=X;this.#X=Q,this.#U=gZ(W),this.#_=j8(J),this.#F=q,this.#V=w,this.#z=M,this.#G=z,this.#x=j!=null&&j!==!1,this.#g=R,this.#O=B===!0,this.#Y=D===!0,this.#w=O9(Z,U),this.#j={itemHeight:this.#w.itemHeight,overscan:O,stickyFolders:b,initialVisibleRowCount:F},this.#Z=new J1({...V,fileTreeSearchMode:Y,initialSearchQuery:G,onSearchChange:A,renaming:j}),this.#m=this.#Z.getSelectionVersion(),this.#P=this.#z==null?null:this.subscribe(()=>{this.#N()})}unmount(){if(this.#J!=null)z3(this.#J),delete this.#J.dataset.fileTreeVirtualizedWrapper,this.#J=void 0;if(this.#B.clearAll(),this.#B.setHost(null),this.#H!=null)delete this.#H.dataset.fileTreeVirtualized,this.#i(this.#H),this.#H=void 0}cleanUp(){this.unmount(),this.#P?.(),this.#P=null,this.#Z.destroy()}getFileTreeContainer(){return this.#H}getItem(X){return this.#Z.getItem(X)}getFocusedItem(){return this.#Z.getFocusedItem()}getFocusedPath(){return this.#Z.getFocusedPath()}getSelectedPaths(){return this.#Z.getSelectedPaths()}getComposition(){return this.#X}getItemHeight(){return this.#w.itemHeight}getDensityFactor(){return this.#w.factor}subscribe(X){let Q=!1;return this.#Z.subscribe(()=>{if(!Q){Q=!0;return}X()})}focusPath(X){this.#Z.focusPath(X)}focusNearestPath(X){return this.#Z.focusNearestPath(X)}add(X){this.#Z.add(X)}batch(X){this.#Z.batch(X)}move(X,Q,Z){this.#Z.move(X,Q,Z)}onMutation(X,Q){return this.#Z.onMutation(X,Q)}setSearch(X){this.#Z.setSearch(X)}openSearch(X){this.#Z.openSearch(X)}closeSearch(){this.#Z.closeSearch()}isSearchOpen(){return this.#Z.isSearchOpen()}getSearchValue(){return this.#Z.getSearchValue()}getSearchMatchingPaths(){return this.#Z.getSearchMatchingPaths()}focusNextSearchMatch(){this.#Z.focusNextSearchMatch()}focusPreviousSearchMatch(){this.#Z.focusPreviousSearchMatch()}startRenaming(X,Q){return this.#Z.startRenaming(X,Q)}remove(X,Q){this.#Z.remove(X,Q)}resetPaths(X,Q){this.#Z.resetPaths(X,Q)}setComposition(X){this.#X=X;let Q=this.#q();if(Q==null)return;this.#D(),i6(Q.wrapper,this.#C())}setGitStatus(X){this.#_=j8(X,this.#_);let Q=this.#q();if(Q==null)return;i6(Q.wrapper,this.#C())}setIcons(X){this.#F=X;let Q=this.#q();if(Q==null)return;this.#L(Q.host,Q.wrapper),i6(Q.wrapper,this.#C())}hydrate({fileTreeContainer:X}){let Q=this.#l(X),Z=this.#f(Q);this.#D(),U3(Z,this.#C())}render({containerWrapper:X,fileTreeContainer:Q}){let Z=this.#l(Q??this.#H,X),Y=this.#f(Z);this.#D(),i6(Y,this.#C())}#t(){return{initialViewportHeight:IZ({initialVisibleRowCount:this.#j.initialVisibleRowCount,itemHeight:this.#j.itemHeight}),itemHeight:this.#j.itemHeight,overscan:this.#j.overscan,stickyFolders:this.#j.stickyFolders}}#C(){return{composition:this.#X,controller:this.#Z,gitStatusByPath:this.#_?.statusByPath,ignoredGitDirectories:this.#_?.ignoredDirectoryPaths,directoriesWithGitChanges:this.#_?.directoriesWithChanges,icons:this.#F,instanceId:this.#U,renamingEnabled:this.#x,renderRowDecoration:this.#G,searchBlurBehavior:this.#g,searchEnabled:this.#O,searchFakeFocus:this.#Y,slotHost:this.#B,...this.#t()}}#q(){let X=this.#H,Q=this.#J;if(X==null||Q==null)return null;return{host:X,wrapper:Q}}#L(X,Q){let Z=X.shadowRoot;if(Z!=null)this.#s(Z),this.#p(Z);this.#c(Q)}#N(){let X=this.#z;if(X==null)return;let Q=this.#Z.getSelectionVersion();if(Q===this.#m)return;this.#m=Q,X(this.#Z.getSelectedPaths())}#D(){let X=this.#X?.header?.render;if(X!=null){this.#B.setSlotContent(m5,X());return}this.#B.setSlotHtml(m5,this.#X?.header?.html??null)}#s(X){let Q=L3(X).find((Y)=>A3(Y)),Z=H3(M9(G6(this.#F).set));if(Z==null)return;if(Q!=null&&Q.outerHTML===Z.outerHTML)return;if(Q!=null)Q.replaceWith(Z);else X.prepend(Z)}#p(X){let Q=L3(X),Z=Q.find((G)=>A3(G)),Y=Q.filter((G)=>G!==Z),J=G6(this.#F).spriteSheet?.trim()??"";if(J.length===0){for(let G of Y)G.remove();return}let W=H3(J);if(W==null){for(let G of Y)G.remove();return}if(Y.length===1&&Y[0].outerHTML===W.outerHTML)return;for(let G of Y)G.remove();X.appendChild(W)}#c(X){let Q=G6(this.#F);if(Q.colored&&A9(Q.set))X.dataset.fileTreeColoredIcons="true";else delete X.dataset.fileTreeColoredIcons}#$(X){let Q=X.querySelector(`style[${s7}]`);if(this.#M==null&&Q instanceof HTMLStyleElement)this.#M=Q;if(this.#V==null||this.#V===""){this.#M?.remove(),this.#M=void 0,this.#I=void 0;return}if(this.#M?.parentNode===X&&this.#I===this.#V)return;if(this.#M??=document.createElement("style"),this.#M.setAttribute(s7,""),this.#M.parentNode!==X)X.appendChild(this.#M);this.#M.textContent=j9(this.#V),this.#I=this.#V}#f(X){if(this.#J!=null)return this.#J;let Q=X.shadowRoot;if(Q==null)throw Error("FileTree requires a shadow root");let Z=Array.from(Q.children).filter((J)=>J instanceof HTMLDivElement&&typeof J.dataset.fileTreeId==="string"&&J.dataset.fileTreeId.length>0),Y=Z.find((J)=>J.dataset.fileTreeId===this.#U)??Z[0];if(Y!=null)this.#U=Y.dataset.fileTreeId??this.#U;if(this.#J=Y??document.createElement("div"),this.#J.dataset.fileTreeId=this.#U,this.#J.dataset.fileTreeVirtualizedWrapper="true",this.#L(X,this.#J),this.#J.parentNode!==Q)Q.appendChild(this.#J);return this.#J}#l(X,Q){let Z=X??this.#H??document.createElement(D5);if(Q!=null&&Z.parentNode!==Q)Q.appendChild(Z);let Y=Z.shadowRoot??Z.attachShadow({mode:"open"});return H7(Z,Y),this.#$(Y),Z.dataset.fileTreeVirtualized="true",Z.style.display="flex",this.#k(Z),this.#B.setHost(Z),this.#H=Z,Z}#k(X){if(X.style.getPropertyValue("--trees-item-height")==="")X.style.setProperty("--trees-item-height",`${String(this.#w.itemHeight)}px`),this.#u=!0;if(X.style.getPropertyValue("--trees-density-override")==="")X.style.setProperty("--trees-density-override",String(this.#w.factor)),this.#h=!0}#i(X){if(this.#u)X.style.removeProperty("--trees-item-height"),this.#u=!1;if(this.#h)X.style.removeProperty("--trees-density-override"),this.#h=!1}};var x7=W6(J6(),1);function mZ(X){let Q=x7.useRef(null);return Q.current??=new O3(X),x7.useEffect(()=>{let Z=Q.current;return()=>{Z?.cleanUp(),Q.current=null}},[]),{model:Q.current}}var o5=W6(J6(),1);function B3(X,Q){if(X===Q)return!0;if(X.length!==Q.length)return!1;for(let Z=0;Z<X.length;Z+=1)if(!Object.is(X[Z],Q[Z]))return!1;return!0}function uZ(X,Q,Z){return Object.is(X,Q)||Z?.(X,Q)===!0}function j3(X,Q,Z){let Y=o5.useRef({hasValue:!1,model:null,selector:null,value:void 0}),J=o5.useCallback((G)=>X.subscribe(G),[X]),W=o5.useCallback(()=>{let G=Y.current,q=Q(X);if(G.model!==X||G.selector!==Q||!G.hasValue)return G.hasValue=!0,G.model=X,G.selector=Q,G.value=q,q;let U=G.value;if(uZ(U,q,Z))return U;return G.value=q,q},[Z,X,Q]);return o5.useSyncExternalStore(J,W,W)}function hZ(X){return j3(X,(Q)=>Q.getSelectedPaths(),B3)}var pZ=/^#(?:[0-9a-f]{3}0|[0-9a-f]{6}00)$/i,cZ=/^0(?:\.0+)?%?$/;function lZ(X){let Q=X.indexOf("(");if(Q<=0||!X.endsWith(")"))return;let Z=X.slice(0,Q).trim();if(!/^(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch|color)$/i.test(Z))return;let Y=X.slice(Q+1,-1).trim();if(Y.length===0)return;let J=Y.lastIndexOf("/");if(J!==-1)return Y.slice(J+1).trim();if(/^(?:rgba|hsla)$/i.test(Z)){let W=Y.split(",");if(W.length===4)return W[3]?.trim()}}function dZ(X){if(X==null)return!1;let Q=X.trim().toLowerCase();if(Q==="transparent")return!0;if(pZ.test(Q))return!0;let Z=lZ(Q);return Z!=null&&cZ.test(Z)}function _3(X){return dZ(X)?void 0:X}function sZ(X){let Q=X.colors??{},Z=Q["sideBar.background"]??Q["editor.background"]??X.bg,Y=Q["sideBar.foreground"]??Q["editor.foreground"]??X.fg,J=Q["sideBar.border"],W=Q["list.activeSelectionForeground"]??Q["sideBar.foreground"],G=Z?.toLowerCase(),q=Q["list.hoverBackground"],U=q?.toLowerCase()===G?void 0:q,A=Q["list.activeSelectionBackground"],M=A?.toLowerCase()===G?Q["list.focusBackground"]??Q["editor.selectionBackground"]:A??Q["editor.selectionBackground"],O=_3(Q["list.focusOutline"])??_3(Q.focusBorder),z=Q["input.background"]??Z,j=Q["input.border"],B=Q["scrollbarSlider.background"],R=Q["sideBarSectionHeader.foreground"]??Y,D=Q["gitDecoration.addedResourceForeground"]??Q["terminal.ansiGreen"]??Q["editorGutter.addedBackground"],b=Q["gitDecoration.modifiedResourceForeground"]??Q["terminal.ansiBlue"]??Q["editorGutter.modifiedBackground"],w=Q["gitDecoration.deletedResourceForeground"]??Q["terminal.ansiRed"]??Q["editorGutter.deletedBackground"],F=X.type==="dark",V={colorScheme:F?"dark":"light",backgroundColor:Z??"",color:Y??"",borderColor:"var(--trees-theme-sidebar-border, light-dark(oklch(0% 0 0 / 0.15), oklch(100% 0 0 / 0.15)))","--trees-theme-sidebar-bg":Z??"","--trees-theme-sidebar-fg":Y??"","--trees-theme-sidebar-header-fg":R??"","--trees-theme-list-active-selection-fg":W??Y??"","--trees-theme-list-hover-bg":U??(F?"rgba(255,255,255,0.08)":"rgba(0,0,0,0.06)"),"--trees-theme-list-active-selection-bg":M??"transparent","--trees-theme-focus-ring":O??Y??"","--trees-theme-input-bg":z??""};if(J!=null&&J!=="")V["--trees-theme-sidebar-border"]=J;if(j!=null&&j!=="")V["--trees-theme-input-border"]=j;if(B!=null&&B!=="")V["--trees-theme-scrollbar-thumb"]=B;if(D!=null&&D!=="")V["--trees-theme-git-added-fg"]=D;if(b!=null&&b!=="")V["--trees-theme-git-modified-fg"]=b;if(w!=null&&w!=="")V["--trees-theme-git-deleted-fg"]=w;return V}export{J6 as O,GX as P,q9 as Q,MX as R,mZ as S,hZ as T,sZ as U};
