/* Magic Mirror Config Sample
 *
 * By Michael Teeuw http://michaelteeuw.nl
 * MIT Licensed.
 */

var config = {
	port: 8080,

	language: 'en',
	timeFormat: 24,
	units: 'metric',

	modules: [
		{
			module: 'alert',
		},
		{
			module: 'clock',
            displayType: 'analog',
			position: 'top_left'
		},
		{
			module: 'calendar',
			header: 'US Holidays',
			position: 'top_left',
			config: {
				calendars: [
					{
						symbol: 'calendar-check-o ',
						url: 'webcal://www.calendarlabs.com/templates/ical/US-Holidays.ics'
					}
				]
			}
		},
		{
			module: 'compliments',
			position: 'bottom_center'
		},
		{
			module: 'currentweather',
			position: 'top_right',
			config: {
	            location: 'Sammamish, WA',
				locationID: '5809402',  //ID from http://www.openweathermap.org
				appid: 'b99041795d2bd64a9c994a0442aee3e9'
			}
		},
		{
			module: 'weatherforecast',
			position: 'top_right',
			header: 'Weather Forecast',
			config: {
	            location: 'Sammamish, WA',
				locationID: '5809402',  //ID from http://www.openweathermap.org
				appid: 'b99041795d2bd64a9c994a0442aee3e9'
			}
	    },
		{
			module: 'newsfeed',
			position: 'bottom_bar',
			config: {
				feeds: [
					{
						title: "Seattle Times",
						url: "http://www.seattletimes.com/seattle-news/feed/"
					}
				],
				showSourceTitle: true,
				showPublishDate: true
			}
		},
        {
            module: 'stocks',
            position: 'top_bar',
            config: {
                stocks: '.DJI,MSFT,AMZN,AAPL,GOOG,TSLA,FB,PONPX', // stock symbols
                updateInterval: 37000 // update interval in milliseconds
            }
        },
        {
            module: 'MMM-PIR-Sensor',
            config: {
                // See 'Configuration options' for more information.
                sensorPIN: 4,
                powerSaving: false
            }
        },
        {
            module: 'hideall'
        },
	]

};

/*************** DO NOT EDIT THE LINE BELOW ***************/
if (typeof module !== 'undefined') {module.exports = config;}
