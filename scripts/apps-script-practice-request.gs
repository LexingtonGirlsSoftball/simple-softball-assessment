// Deploy this as a Google Apps Script Web App (Deploy > New deployment > Web app,
// execute as "Me", access "Anyone") and paste the resulting /exec URL into
// PRACTICE_REQUEST_WEBHOOK_URL in GoogleFieldCalendar.html.
// Payload shape sent by the page (see submitPracticeRequestToWebhook in GoogleFieldCalendar.html).

var CALENDAR_ID = '54b6ccd7fdf7a8acc9ab44b1c8281023e228fd8eb6d9a6f694340f4dd04ec65e@group.calendar.google.com';

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var calendar = CalendarApp.getCalendarById(CALENDAR_ID);
    if (!calendar) throw new Error('Calendar not found or not accessible to this script');

    var title = data.title;
    var startTime = new Date(data.firstPracticeDate + 'T' + data.startTime + ':00');
    var endTime = new Date(data.firstPracticeDate + 'T' + data.endTime + ':00');
    var untilDate = new Date(data.untilDate + 'T23:59:59');

    var recurrence = CalendarApp.newRecurrence().addWeeklyRule().until(untilDate);

    var descriptionLines = [
      'League request period: ' + data.periodLabel,
      'Practice day: ' + data.dayLabel,
      'Time slot: ' + data.timeLabel,
      'Requested location: ' + data.field,
      '',
      'Coach: ' + data.coachLastName,
      'Contact email: ' + (data.coachEmail || 'Not provided'),
      'Contact phone: ' + (data.coachPhone || 'Not provided'),
      'Notes: ' + (data.notes || 'None'),
      '',
      data.requestType === 'travel'
        ? 'Valid insurance must be emailed to girlssoftballlgssc@gmail.com.'
        : 'Submit this event for approval from the calendar admins.'
    ];

    var series = calendar.createEventSeries(title, startTime, endTime, recurrence, {
      location: '1159 Nazareth Rd, Lexington, SC',
      description: descriptionLines.join('\n')
    });
    // Color-code pending requests (Peacock) so admins can spot them at a glance.
    series.setColor(CalendarApp.EventColor.PALE_BLUE);

    return ContentService.createTextOutput(JSON.stringify({ status: 'success' }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
