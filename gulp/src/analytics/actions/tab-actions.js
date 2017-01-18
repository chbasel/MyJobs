import {createAction} from 'redux-actions';

export const switchActiveTab = createAction('SWITCH_ACTIVE_TAB');
export const breadCrumbSwitchTab = createAction('BREADCRUMB_SWITCH_ACTIVE_TAB');
export const storeDeletedTab = createAction('STORE_DELETED_TAB');
export const removeSelectedTab = createAction('REMOVE_SELECTED_TAB');
export const setCurrentRange = createAction('SET_CURRENT_RANGE');

/**
 * This action switches the current tab to a tab selected using the tabid
 */
export function doSwitchActiveTab(tabId) {
  return (dispatch, getState) => {
    dispatch(switchActiveTab(tabId));
    let rangeDate;
    getState().pageLoadData.navigation.map((nav) => {
      if (nav.active) {
        rangeDate = nav.currentDateRange;
      }
    });
    dispatch(setCurrentRange(rangeDate));
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
    getState().pageLoadData.navigation.map((nav) => {
      if (nav.crumbs.length === 1 && nav.crumbs[0] === crumb) {
        tabId = nav.navId;
      }
      if (nav.crumbs.indexOf(crumb)) {
        if (nav.crumbs[nav.crumbs.length - 1] === crumb) {
          tabId = nav.navId;
        }
      }
    });
    dispatch(switchActiveTab(tabId));
  };
}
