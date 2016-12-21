/**
 * This action switches the current tab to a tab selected using the tabid
 */
export function switchActiveTab(tabId) {
  return {
    type: 'SWITCH_ACTIVE_TAB',
    payload: tabId,
  };
}

/**
 * This action removes a specific tab by clicking the x button on the tab using the tabid
 */
export function removeSelectedTab(tabId) {
  return {
    type: 'REMOVE_SELECTED_TAB',
    payload: tabId,
  };
}
