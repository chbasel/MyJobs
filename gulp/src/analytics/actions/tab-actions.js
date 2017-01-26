import {createAction} from 'redux-actions';
import {markNavLoadingAction} from '../../common/actions/loading-actions';
import {errorAction} from '../../common/actions/error-actions';

export const switchActiveTab = createAction('SWITCH_ACTIVE_TAB');
export const breadCrumbSwitchTab = createAction('BREADCRUMB_SWITCH_TAB');
export const restoreDeletedTab = createAction('RESTORE_DELETED_TAB');
export const storeDeletedTab = createAction('STORE_DELETED_TAB');
export const deleteStoredDeletedTab = createAction('DELETE_STORED_DELETED_TAB');
export const removeSelectedTab = createAction('REMOVE_SELECTED_TAB');
export const setCurrentRange = createAction('SET_CURRENT_RANGE');
export const updateSwitchedTabData = createAction('UPDATE_SWITCHED_TAB_DATA');

/**
 * This action switches the current tab to a tab selected using the tabid
 */
export function doSwitchActiveTab(tabId) {
  return async (dispatch, getState, {api}) => {
    try {
      dispatch(switchActiveTab(tabId));
      let rangeDate;
      const stateNavigation = getState().pageLoadData.navigation;
      const globalStart = getState().pageLoadData.globalStartDate;
      const globalEnd = getState().pageLoadData.globalEndDate;
      // Loop through the current states navigation and check to see if the global date has changed
      for (let i = 0; i < stateNavigation.length; i++) {
        if (stateNavigation[i].active) {
          if (stateNavigation[i].startDate !== globalStart || stateNavigation[i].endDate !== globalEnd) {
            dispatch(markNavLoadingAction(true));
            const storedFilters = stateNavigation[i].activeFilters;
            const currentReport = getState().pageLoadData.activeReport;
            const storedDates = {
              startDate: globalStart,
              endDate: globalEnd,
            };
            const selectedFilterData = await api.getSelectedFilterData(storedFilters, currentReport, storedDates);
            const updatedData = {
              data: selectedFilterData,
              date: storedDates,
            };
            console.log(updatedData);
            dispatch(updateSwitchedTabData(updatedData));
            dispatch(markNavLoadingAction(false));
          }
          rangeDate = nav.currentDateRange;
        }
      }
      dispatch(setCurrentRange(rangeDate));
    } catch (error) {
      dispatch(errorAction(error.message));
    }
  };
}

/**
 * This action removes a specific tab by clicking the x button on the tab using the tabid
 */
export function doRemoveSelectedTab(tabId) {
  return (dispatch, getState) => {
    const selectedTab = getState().pageLoadData.navigation.filter(tab => tab.navId === tabId);
    if (selectedTab[0].active) {
      let maxNav = 0;
      getState().pageLoadData.navigation.map(tab => {
        if (!tab.active) {
          maxNav = tab.navId > maxNav ? tab.navId : maxNav;
        }
      });
      dispatch(switchActiveTab(maxNav));
    }
    // Storing the deleted tab before it's removed from the state
    dispatch(storeDeletedTab(selectedTab[0]));
    dispatch(removeSelectedTab(tabId));
  };
}

/**
 * This action will also switch the current tab depending on which breadcrumb you actually click on
 */
export function doBreadCrumbSwitchTab(crumb) {
  return (dispatch, getState) => {
    let tabId;
    let index;
    const navigation = getState().pageLoadData.navigation;
    // Looping through the deleted tabs to see if the crumbs match in case we need to re add the tab back as an undo function
    if (getState().pageLoadData.deletedNavigation.length > 0) {
      getState().pageLoadData.deletedNavigation.map((deleted) => {
        if (deleted.crumbs[deleted.crumbs.length - 1] === crumb) {
          for (let i = 0; i < navigation.length; i++) {
            if (navigation[i].navId === deleted.navId + 1) {
              index = i;
              break;
            } else if (navigation[i].navId === deleted.navId - 1) {
              index = i + 1;
              break;
            } else {
              index = 1;
            }
          }
          dispatch(restoreDeletedTab({deleted: deleted, index: index}));
          dispatch(deleteStoredDeletedTab(deleted));
          tabId = deleted.navId;
        } else {
          navigation.map((nav) => {
            if (nav.crumbs.length === 1 && nav.crumbs[0] === crumb) {
              tabId = 1;
            }
            if (nav.crumbs[nav.crumbs.length - 1] === crumb) {
              tabId = nav.navId;
            }
          });
        }
      });
    } else {
      navigation.map((nav) => {
        if (nav.crumbs.length === 1 && nav.crumbs[0] === crumb) {
          tabId = 1;
        }
        if (nav.crumbs[nav.crumbs.length - 1] === crumb) {
          tabId = nav.navId;
        }
      });
    }
    dispatch(switchActiveTab(tabId));
  };
}
