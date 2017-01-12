import {createAction} from 'redux-actions';
import {markNavLoadingAction} from '../../common/actions/loading-actions';
import {errorAction} from '../../common/actions/error-actions';

export const setSelectedFilterData = createAction('SET_SELECTED_FILTER_DATA');
export const storeActiveFilter = createAction('STORE_ACTIVE_FILTER');

/**
 * This action stores the active filters for sending back to the API in other request
 */
export function doStoreActiveFilter(type, value) {
  return (dispatch) => {
    dispatch(storeActiveFilter({type: type, value: value}));
  };
}

/**
 * This action will get and set the current applied table filter when a filter is clicked inside of the table
 */
export function doGetSelectedFilterData(tableValue, typeValue) {
  return async (dispatch, getState, {api}) => {
    try {
      dispatch(markNavLoadingAction(true));
      dispatch(doStoreActiveFilter(typeValue, tableValue));

      // Storing the current filters inside of the state to send off in the request to the API
      const storedFilters = [];
      // Storing the dates in order to update the reducer with them
      let storedDates;
      getState().pageLoadData.activeFilters.map((filter) => {
        storedFilters.push(filter);
      });
      console.log(storedFilters);
      getState().pageLoadData.navigation.map((nav) => {
        if (nav.active) {
          storedDates = {
            startDate: nav.startDate,
            endDate: nav.endDate,
          };
        }
      });
      const tabFilters = getState().pageLoadData.activeFilters;
      const range = getState().pageLoadData.stateCustomRange;
      // Grabbing the current report selected from the state to send to the API
      const currentReport = getState().pageLoadData.activeReport;
      const selectedFilterData = await api.getSelectedFilterData(tableValue, typeValue, storedFilters, currentReport, storedDates);
      // Creating object from the filter selection data to send off to the reducer to update
      const navFilterData = {
        data: selectedFilterData,
        date: storedDates,
        tabFilter: tabFilters,
        loadRange: range,
      };
      dispatch(setSelectedFilterData(navFilterData));
      dispatch(markNavLoadingAction(false));
    } catch (error) {
      dispatch(errorAction(error.message));
    }
  };
}
