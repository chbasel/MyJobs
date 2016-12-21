import {createAction} from 'redux-actions';
import {markPageLoadingAction} from '../../common/actions/loading-actions';

export const setPageData = createAction('SET_PAGE_DATA');
export const setPrimaryDimensions = createAction('SET_PRIMARY_DIMENSIONS');
export const setSelectedFilterData = createAction('SET_SELECTED_FILTER_DATA');
export const storeInitialReport = createAction('STORE_INITIAL_REPORT');
export const setCurrentMonth = createAction('SET_CURRENT_MONTH');
export const setCurrentYear = createAction('SET_CURRENT_YEAR');
export const setCurrentDay = createAction('SET_CURRENT_DAY');

/**
 * This action does all of the necessary steps for getting the page data that will be loaded when the app first boots
 */
export function doGetPageData(start, end, currentMonth, currentDay, currentYear) {
  return async (dispatch, _, {api}) => {
    dispatch(markPageLoadingAction(true));
    const rawPageData = await api.getInitialPageData(start, end);
    // Creating object of data coming back from the API along with the starting and ending date to send to reducer
    const allLoadData = {
      startDate: start,
      endDate: end,
      pageData: rawPageData,
    };
    const dimensionData = await api.getPrimaryDimensions();
    const reportType = await api.getStartingPointReport();
    dispatch(setPageData(allLoadData));
    dispatch(setCurrentMonth(currentMonth));
    dispatch(setCurrentYear(currentYear));
    dispatch(setCurrentDay(currentDay));
    dispatch(setPrimaryDimensions(dimensionData));
    dispatch(storeInitialReport(reportType));
    dispatch(markPageLoadingAction(false));
  };
}
