import {createAction} from 'redux-actions';
import {markNavLoadingAction} from '../../common/actions/loading-actions';
import {errorAction} from '../../common/actions/error-actions';

export const markUpdateMessageShown = createAction('MARK_UPDATE_MESSAGE_SHOWN');
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
      const stateNavigation = getState().pageLoadData.navigation;
      const globalStart = getState().pageLoadData.globalStartDate;
      const globalEnd = getState().pageLoadData.globalEndDate;
      let dateChanged = false;
      let storedFilters;
      // Loop through the current states navigation and check to see if the global date has changed
      for (let i = 0; i < stateNavigation.length; i++) {
        if (stateNavigation[i].active) {
          if (stateNavigation[i].startDate !== globalStart || stateNavigation[i].endDate !== globalEnd) {
            dateChanged = true;
            storedFilters = stateNavigation[i].activeFilters;
          }
        }
      }
      if (dateChanged) {
        dispatch(markNavLoadingAction(true));
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
        dispatch(updateSwitchedTabData(updatedData));
        dispatch(markNavLoadingAction(false));
        dispatch(markUpdateMessageShown(true));
        setTimeout(() => {dispatch(markUpdateMessageShown(false));}, 3000);
      }
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
  return async (dispatch, getState, {api}) => {
    let tabId;
    let index;
    const navigation = getState().pageLoadData.navigation;
    const deletedNavigation = getState().pageLoadData.deletedNavigation;
    const currentGlobalStartDate = getState().pageLoadData.globalStartDate;
    const currentGlobalEndDate = getState().pageLoadData.globalEndDate;
    const storedDates = {
      startDate: currentGlobalStartDate,
      endDate: currentGlobalEndDate,
    };
    const currentReport = getState().pageLoadData.activeReport;
    let dateChanged = false;
    let storedFilters;
    let deletedNavData;
    // Looping through the deleted tabs to see if the crumbs match in case we need to re add the tab back as an undo function
    if (deletedNavigation.length > 0) {
      for (let i = 0; i < deletedNavigation.length; i++) {
        if (deletedNavigation[i].crumbs[deletedNavigation[i].crumbs.length - 1] === crumb) {
          for (let n = 0; n < navigation.length; n++) {
            if (navigation[n].navId === deletedNavigation[i].navId + 1) {
              index = n;
              break;
            } else if (navigation[n].navId === deletedNavigation[i].navId - 1) {
              index = n + 1;
              break;
            } else {
              index = 1;
            }
          }
          if (deletedNavigation[i].startDate !== currentGlobalStartDate || deletedNavigation[i].endDate !== currentGlobalEndDate) {
            dateChanged = true;
            storedFilters = deletedNavigation[i].activeFilters;
            deletedNavData = deletedNavigation[i];
          } else {
            dispatch(restoreDeletedTab({deleted: deletedNavigation[i], index: index}));
          }
          dispatch(deleteStoredDeletedTab(deletedNavigation[i]));
          tabId = deletedNavigation[i].navId;
        } else {
          for (let p = 0; p < navigation.length; p++) {
            if (navigation[p].crumbs.length === 1 && navigation[p].crumbs[0] === crumb) {
              tabId = 1;
            }
            if (navigation[p].crumbs[navigation[p].crumbs.length - 1] === crumb) {
              tabId = navigation[p].navId;
            }
          }
        }
      }
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
    if (dateChanged) {
      dispatch(markNavLoadingAction(true));
      const updateDeleted = await api.getSelectedFilterData(storedFilters, currentReport, storedDates);
      const newUpdateDeleted = {
        ...deletedNavData,
        startDate: currentGlobalStartDate,
        endDate: currentGlobalEndDate,
        PageLoadData: updateDeleted,
      };
      dispatch(restoreDeletedTab({deleted: newUpdateDeleted, index: index}));
      dispatch(markNavLoadingAction(false));
      dispatch(markUpdateMessageShown(true));
      setTimeout(() => {dispatch(markUpdateMessageShown(false));}, 3000);
    }
    dispatch(switchActiveTab(tabId));
  };
}
