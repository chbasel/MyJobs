import {Calendar} from 'calendar-base';
import {pairs, merge} from 'lodash-compat/object';
import {chunk, zipObject, zipWith} from 'lodash-compat/array';
import {map} from 'lodash-compat/collection';

export const monthsArray = [
  {value: '1', display: 'January'},
  {value: '2', display: 'February'},
  {value: '3', display: 'March'},
  {value: '4', display: 'April'},
  {value: '5', display: 'May'},
  {value: '6', display: 'June'},
  {value: '7', display: 'July'},
  {value: '8', display: 'August'},
  {value: '9', display: 'September'},
  {value: '10', display: 'October'},
  {value: '11', display: 'November'},
  {value: '12', display: 'December'},
];

function changeKey(obj, from, to) {
  return zipObject(map(pairs(obj), p => {
    const key = p[0];
    const value = p[1];
    if (key === from) {
      return [to, value];
    }
    return [key, value];
  }));
}

export function calendarDays(year, month, selected, other) {
  const rangeCal = new Calendar({siblingMonths: true, weekStart: 1});
  const selectCal = new Calendar({siblingMonths: true, weekStart: 1});

  if (selected && other) {
    let begin;
    let end;
    const diff = Calendar.diff(selected, other);
    if (diff < 0) {
      begin = selected;
      end = other;
    } else {
      begin = other;
      end = selected;
    }

    rangeCal.setStartDate(begin);
    rangeCal.setEndDate(end);
    selectCal.setDate(selected);
  } else if (selected) {
    selectCal.setDate(selected);
  }

  const rangeDays = rangeCal.getCalendar(year, month);
  const selectDays = selectCal.getCalendar(year, month);

  const fixedRange = map(rangeDays, d => changeKey(d, 'selected', 'inRange'));
  const days = zipWith(fixedRange, selectDays, (r, s) => merge({}, r, s));

  return chunk(days, 7);
}
