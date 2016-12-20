import {createAction} from 'redux-actions';
import {markNavLoadingAction} from '../../common/actions/loading-actions';

export const setSelectedFilterData = createAction('SET_SELECTED_FILTER_DATA');
export const storeActiveFilter = createAction('STORE_ACTIVE_FILTER');

/**
 * This action stores the active filters for sending back to the API in other request
 */
export function doStoreActiveFilter(type, value) {
  return async (dispatch) => {
    dispatch(storeActiveFilter({type: type, value: value}));
  };
}

/**
 * This action will get and set the current applied table filter when a filter is clicked inside of the table
 */
export function doGetSelectedFilterData(tableValue, typeValue) {
  return async (dispatch, getState, {api}) => {
    dispatch(markNavLoadingAction(true));
    dispatch(doStoreActiveFilter(typeValue, tableValue));
    // Storing the current filters inside of the state to send off in the request to the API
    const storedFilters = [];
    let storedDates;
    getState().pageLoadData.activeFilters.map((filter) => {
      storedFilters.push(filter);
    });
    getState().pageLoadData.navigation.map((nav) => {
      if (nav.active) {
        storedDates = {
          startDate: nav.startDate,
          endDate: nav.endDate,
        };
      }
    });
    console.log('Current State: ', getState());
    console.log('Stored Dates: ', storedDates);
    const currentReport = getState().pageLoadData.activeReport;
    const selectedFilterData = await api.getSelectedFilterData(tableValue, typeValue, storedFilters, currentReport, storedDates);
    const navFilterData = {
      data: selectedFilterData,
      date: storedDates,
    };
    dispatch(setSelectedFilterData(navFilterData));
    dispatch(markNavLoadingAction(false));
  };
}
