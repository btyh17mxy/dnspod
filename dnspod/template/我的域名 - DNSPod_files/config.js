// sea.js config base bug??
var base = (www_head == '' ? window.location.protocol+'//'+window.location.host : www_head) + '/yantai/';
// Change version (xxxxx.v\d+) after modified to clear cache!
var alias = {
      // modules.seajs.com
      'jquery':'js/libs/jquery/1.7.2/jquery',
      '$':'js/libs/jquery/1.7.2/jquery',
      'underscore':'js/libs/underscore/1.5.2/underscore',
      'backbone':'js/libs/backbone/0.9.9/backbone',
      'mustache':'js/libs/mustache/0.4.0/mustache',
      'handlebars':'js/libs/handlebars/1.0.0/handlebars',
      'json': 'js/libs/json/1.0.2/json',
      'cookie': 'js/libs/cookie/1.0.2/cookie',
      'moment': 'js/libs/moment/1.6.2/moment',

      // all plugins
      'plugins':'js/modules/plugins',
      'autocomplete':'js/3rd-libs/jquery.autocomplete',
      'highcharts':'js/3rd-libs/highcharts/highcharts.src',
      'highstock':'js/3rd-libs/highstock/1.2.5/highstock',
      'highexport':'js/3rd-libs/highstock/1.2.5/exporting',
      'cache':'js/3rd-libs/cache',
      'highchartsexporting':'js/3rd-libs/highcharts/modules/exporting.src',
      'moment_with_lang': 'js/3rd-libs/moment-lang.zh-cn',
      'qrcode': 'js/3rd-libs/jquery.qrcode.min',
      'pagination': 'js/3rd-libs/jquery.simplePagination',
      'select2': 'js/3rd-libs/select2/3.2/select2.min',
      'inputSuggest': 'js/3rd-libs/inputSuggest',


      // modules
      'domain':'js/modules/domain',
      'record':'js/modules/record',
      'monitor':'js/modules/monitor',
      'monitor_huhao':'js/modules/monitor.huhao',
      'dmonitor':'js/modules/dmonitor',
      'service':'js/modules/service',
      'user':'js/modules/user',
      'domain.settingline':'js/modules/domain.settingline',
      'domain.setting':'js/modules/domain.setting',
      'domain.statistics':'js/modules/domain.statistics',
      'account.setting':'js/modules/account.setting',
      'popup':'js/modules/popup',
      'modal':'js/modules/modal',
      'util':'js/modules/util',
      'shopping':'js/modules/shopping',
      'cart':'js/modules/cart',

      // css
      'global.css': 'css/global.css',
      'record_select2.css': 'css/select2.css',
      'select2.css': 'js/3rd-libs/select2/3.2/select2.css',
      'plans.css': 'css/plans.css'

   };

for (var a in alias) {
   alias[a] = base + alias[a];
}

seajs.config({
   alias: alias,
   map: [
      [ /^(.*\/yantai\/.*\.(?:css|js))(?:.*)$/i, '$1?v='+www_version ] // timestamp here, clean the cache
   ],
   preload: [
    this.JSON ? '' : 'json'
  ]
});

// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function(){
  log.history = log.history || [];   // store logs to an array for reference
  log.history.push(arguments);
  if(this.console) {
   arguments.callee = arguments.callee.caller;
   var newarr = [].slice.call(arguments);
   (typeof console.log === 'object' ? log.apply.call(console.log, console, newarr) : console.log.apply(console, newarr));
  }
};
// make it safe to use console.log always
(function(b){function c(){}for(var d="assert,count,debug,dir,dirxml,error,exception,group,groupCollapsed,groupEnd,info,log,timeStamp,profile,profileEnd,time,timeEnd,trace,warn".split(","),a;a=d.pop();){b[a]=b[a]||c}})((function(){try
{console.log();return window.console;}catch(err){return window.console={};}})());
 
