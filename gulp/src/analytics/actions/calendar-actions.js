import {createAction} from 'redux-actions';
import {markNavLoadingAction} from '../../common/actions/loading-actions';

export const setSelectedMonth = createAction('SET_SELECTED_MONTH');
export const setSelectedYear = createAction('SET_SELECTED_YEAR');
export const setSelectedDay = createAction('SET_SELECTED_DAY');
export const setSelectedRange = createAction('SET_SELECTED_RANGE');

/**
 * This action sets the current month selected from the Calendar ONLY
 */
export function doSetSelectedMonth(month) {
  return async(dispatch) => {
    const currentMonth = month;
    dispatch(setSelectedMonth(currentMonth));
  };
}
/**
 * This action sets the current year selected from the Calendar ONLY
 */
export function doSetSelectedYear(year) {
  return async(dispatch) => {
    const currentYear = year;
    dispatch(setSelectedYear(currentYear));
  };
}
/**
 * This action sets the current day selected from the Calendar ONLY
 */
export function doSetSelectedDay(day) {
  return async(dispatch) => {
    const currentDay = day.day;
    dispatch(setSelectedDay(currentDay));
  };
}
/**
 * This action sets the selected range from the quick range selections, not the Calendar
 */
export function doSetSelectedRange(start, end, mainDimension, activeFilters) {
  return async(dispatch, _, {api}) => {
    dispatch(markNavLoadingAction(true));
    const currentStartRange = start;
    const currentEndRange = end;
    const currentDimension = mainDimension;
    const currentFilters = activeFilters;
    const rangeData = await api.getDateRangeData(currentStartRange, currentEndRange, currentDimension, currentFilters);
    // Creating object to send to reducer with date range data and start and end dates
    const updatedRangeData = {
      data: rangeData,
      startDate: start,
      endDate: end,
    };
    dispatch(setSelectedRange(updatedRangeData));
    dispatch(markNavLoadingAction(false));
  };
}
