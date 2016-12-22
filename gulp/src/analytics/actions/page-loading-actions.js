import {createAction} from 'redux-actions';
import {markPageLoadingAction} from '../../common/actions/loading-actions';

export const setPageData = createAction('SET_PAGE_DATA');
export const setPrimaryDimensions = createAction('SET_PRIMARY_DIMENSIONS');
export const setSelectedFilterData = createAction('SET_SELECTED_FILTER_DATA');
export const storeInitialReport = createAction('STORE_INITIAL_REPORT');
export const setCurrentEndMonth = createAction('SET_CURRENT_END_MONTH');
export const setCurrentEndYear = createAction('SET_CURRENT_END_YEAR');
export const setCurrentEndDay = createAction('SET_CURRENT_END_DAY');
export const setCurrentStartMonth = createAction('SET_CURRENT_START_MONTH');
export const setCurrentStartYear = createAction('SET_CURRENT_START_YEAR');
export const setCurrentStartDay = createAction('SET_CURRENT_START_DAY');

/**
 * This action does all of the necessary steps for getting the page data that will be loaded when the app first boots
 */
export function doGetPageData(start, end, currentEndMonth, currentEndDay, currentEndYear, currentStartMonth, currentStartDay, currentStartYear) {
  return async (dispatch, _, {api}) => {
    dispatch(markPageLoadingAction(true));
    const rawPageData = await api.getInitialPageData(start, end);
    const splitEnd = end.split(' ')[0];
    const splitStart = start.split(' ')[0];
    const range = splitStart + ' - ' + splitEnd;
    // Creating object of data coming back from the API along with the starting and ending date to send to reducer
    const allLoadData = {
      startDate: start,
      endDate: end,
      pageData: rawPageData,
      loadRange: range,
    };
    const dimensionData = await api.getPrimaryDimensions();
    const reportType = await api.getStartingPointReport();
    dispatch(setPageData(allLoadData));
    dispatch(setCurrentEndMonth(currentEndMonth));
    dispatch(setCurrentEndYear(currentEndYear));
    dispatch(setCurrentEndDay(currentEndDay));
    dispatch(setCurrentStartMonth(currentStartMonth));
    dispatch(setCurrentStartYear(currentStartYear));
    dispatch(setCurrentStartDay(currentStartDay));
    dispatch(setPrimaryDimensions(dimensionData));
    dispatch(storeInitialReport(reportType));
    dispatch(markPageLoadingAction(false));
  };
}
