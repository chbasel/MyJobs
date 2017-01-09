import {createAction} from 'redux-actions';
import {markPageLoadingAction} from '../../common/actions/loading-actions';
import {markNavLoadingAction} from '../../common/actions/loading-actions';
import {errorAction} from '../../common/actions/error-actions';

export const setPrimaryDimensions = createAction('SET_PRIMARY_DIMENSIONS');
export const switchMainDimension = createAction('SWITCH_MAIN_DIMENSION');
export const setMainDimension = createAction('SET_MAIN_DIMENSION');
export const storeActiveReport = createAction('STORE_ACTIVE_REPORT');

/**
 * This action sets the current month selected from the Calendar
 */
// Action for loading the initial primary dimensions
export function doGetPrimaryDimensions() {
  return async (dispatch, _, {api}) => {
    try {
      dispatch(markPageLoadingAction(true));
      const dimensionData = await api.getPrimaryDimensions();
      dispatch(setPrimaryDimensions(dimensionData));
      dispatch(markPageLoadingAction(false));
    } catch (error) {
      dispatch(errorAction(error.message));
    }
  };
}

/**
 * This action gets the data when the primary dimensions in the sidebar are changed
 */
export function doSwitchMainDimension(mainDimension, start, end) {
  return async (dispatch, getState, {api}) => {
    try {
      dispatch(markNavLoadingAction(true));
      dispatch(storeActiveReport(mainDimension));
      const currentDimensionData = await api.getMainDimensionData(mainDimension, start, end);
      const splitEnd = end.split(' ')[0];
      const splitStart = start.split(' ')[0];
      const range = splitStart + ' - ' + splitEnd;
      // Creating object of data coming back from the API along with the starting and ending date to send to reducer when the main dimension is changed
      const allLoadData = {
        startDate: start,
        endDate: end,
        pageData: currentDimensionData,
        loadRange: range,
      };
      dispatch(switchMainDimension(allLoadData));
      dispatch(markNavLoadingAction(false));
      dispatch(setMainDimension(mainDimension));
    } catch (error) {
      dispatch(errorAction(error.message));
    }
  };
}
