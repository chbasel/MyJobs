import {createAction} from 'redux-actions';

export const switchActiveTab = createAction('SWITCH_ACTIVE_TAB');
export const removeSelectedTab = createAction('REMOVE_SELECTED_TAB');

/**
 * This action switches the current tab to a tab selected using the tabid
 */
export function doSwitchActiveTab(tabId) {
  return (dispatch) => {
    dispatch(switchActiveTab(tabId));
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
    dispatch(removeSelectedTab(tabId));
  };
}
