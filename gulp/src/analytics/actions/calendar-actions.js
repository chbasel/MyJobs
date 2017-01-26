import {createAction} from 'redux-actions';
import {markNavLoadingAction} from '../../common/actions/loading-actions';
import {errorAction} from '../../common/actions/error-actions';
import {markUpdateMessageShown} from './tab-actions';

export const setSelectedEndMonth = createAction('SET_SELECTED_END_MONTH');
export const setSelectedEndYear = createAction('SET_SELECTED_END_YEAR');
export const setSelectedEndDay = createAction('SET_SELECTED_END_DAY');
export const setSelectedStartMonth = createAction('SET_SELECTED_START_MONTH');
export const setSelectedStartYear = createAction('SET_SELECTED_START_YEAR');
export const setSelectedStartDay = createAction('SET_SELECTED_START_DAY');
export const setSelectedRange = createAction('SET_SELECTED_RANGE');
export const setCustomRange = createAction('SET_CUSTOM_RANGE');

/**
 * This action sets the current month selected from the  Ending Date Calendar ONLY
 */
export function doSetSelectedEndMonth(month) {
  return async(dispatch) => {
    try {
      dispatch(setSelectedEndMonth(month));
    } catch (error) {
      dispatch(errorAction(error.message));
    }
  };
}
/**
 * This action sets the current month selected from the Starting Date Calendar ONLY
 */
export function doSetSelectedStartMonth(month) {
  return async(dispatch) => {
    try {
      dispatch(setSelectedStartMonth(month));
    } catch (error) {
      dispatch(errorAction(error.message));
    }
  };
}
/**
 * This action sets the current year selected from the Ending Date Calendar ONLY
 */
export function doSetSelectedEndYear(year) {
  return async(dispatch) => {
    try {
      dispatch(setSelectedEndYear(year));
    } catch (error) {
      dispatch(errorAction(error.message));
    }
  };
}
/**
 * This action sets the current year selected from the Starting Date Calendar ONLY
 */
export function doSetSelectedStartYear(year) {
  return async(dispatch) => {
    try {
      dispatch(setSelectedStartYear(year));
    } catch (error) {
      dispatch(errorAction(error.message));
    }
  };
}
/**
 * This action sets the current day selected from the  Ending Date Calendar ONLY
 */
export function doSetSelectedEndDay(day) {
  return async(dispatch) => {
    try {
      const currentDay = day.day;
      dispatch(setSelectedEndDay(currentDay));
    } catch (error) {
      dispatch(errorAction(error.message));
    }
  };
}
/**
 * This action sets the current day selected from the Starting Date Calendar ONLY
 */
export function doSetSelectedStartDay(day) {
  return async(dispatch) => {
    try {
      const currentDay = day.day;
      dispatch(setSelectedStartDay(currentDay));
    } catch (error) {
      dispatch(errorAction(error.message));
    }
  };
}
/**
 * This action sets the selected range from the quick range selections, not the Calendar
 */
export function doSetSelectedRange(start, end, mainDimension, activeFilters) {
  return async(dispatch, _, {api}) => {
    try {
      dispatch(markNavLoadingAction(true));
      const messageDelay = setTimeout(() => {dispatch(markUpdateMessageShown(false));}, 3000);
      const currentStartRange = start;
      const currentEndRange = end;
      const currentDimension = mainDimension;
      const currentFilters = activeFilters;
      const rangeData = await api.getDateRangeData(currentStartRange, currentEndRange, currentDimension, currentFilters);
      const splitEnd = end.split(' ')[0];
      const splitStart = start.split(' ')[0];
      const range = splitStart + ' - ' + splitEnd;
      // Creating object to send to reducer with date range data and start and end dates
      const updatedRangeData = {
        data: rangeData,
        startDate: start,
        endDate: end,
        loadRange: range,
      };
      dispatch(setSelectedRange(updatedRangeData));
      dispatch(markNavLoadingAction(false));
      dispatch(markUpdateMessageShown(true));
      messageDelay();
    } catch (err) {
      dispatch(errorAction(err.message));
    }
  };
}
/**
 * This action sets the custom range selected from the Range Calendars
 */
export function doSetCustomRange(start, end, mainDimension, activeFilters) {
  return async(dispatch, _, {api}) => {
    try {
      dispatch(markNavLoadingAction(true));
      const messageDelay = setTimeout(() => {dispatch(markUpdateMessageShown(false));}, 3000);
      const currentStartRange = start;
      const currentEndRange = end;
      const currentDimension = mainDimension;
      const currentFilters = activeFilters;
      const rangeData = await api.customDateRangeData(currentStartRange, currentEndRange, currentDimension, currentFilters);
      const splitEnd = end.split(' ')[0];
      const splitStart = start.split(' ')[0];
      const range = splitStart + ' - ' + splitEnd;
      // Creating object to send to reducer with date range data and start and end dates
      const updatedRangeData = {
        data: rangeData,
        startDate: start,
        endDate: end,
        loadRange: range,
      };
      dispatch(setCustomRange(updatedRangeData));
      dispatch(markNavLoadingAction(false));
      dispatch(markUpdateMessageShown(true));
      messageDelay();
    } catch (err) {
      dispatch(errorAction(err.message));
    }
  };
}
