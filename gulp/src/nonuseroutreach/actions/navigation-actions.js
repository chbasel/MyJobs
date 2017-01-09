import {createAction} from 'redux-actions';

export const setPageAction = createAction(
  'SET_PAGE',
  (page) => ({page}));

export const setWorkflowStateChoicesAction = createAction('SET_WORKFLOW_CHOICES');
export const updateTermFilterAction = createAction('SET_TERM_FILTER');
export const updateWorkflowFilterAction = createAction('SET_WORKFLOW_FILTER');
export const setFiltersActiveAction = createAction('SET_FILTERS_ACTIVE');
export const filterRecordsAction = createAction('FILTER_RECORDS');

/* doGetWorkflowStateChoices
  Retrieves possible workflow states for use in dropdowns
 */
export function doGetWorkflowStateChoices() {
  return async (dispatch, _, {api}) => {
    const rawChoices = await api.getWorkflowStates();
    const formattedChoices = [
      {
        value: 'All',
        display: 'All',
        render: () => '',
      },
    ];
    for (let i = 0; i < rawChoices.length; i++) {
      formattedChoices.push({
        value: rawChoices[i].name,
        display: rawChoices[i].name,
        render: () => '',
      });
    }
    dispatch(setWorkflowStateChoicesAction(formattedChoices));
  };
}

/* doFilterRecords
  Adds or updates filtered records object for display
 */
export function doFilterRecords() {
  return async (dispatch, getState) => {
    let filteredRecords = getState().records;
    let filtersActive = false;
    const termFilter = getState().navigation.termFilter;
    const workflowFilter = getState().navigation.workflowFilter;
    if (workflowFilter !== 'All') {
      filtersActive = true;
      filteredRecords = filteredRecords.filter(record => record.currentWorkflowState === workflowFilter);
    }
    if (termFilter) {
      filtersActive = true;
      const filterRegex = new RegExp(termFilter, 'i');
      filteredRecords = filteredRecords.filter(record => (
        record.outreachEmail.search(filterRegex) !== -1 ||
          record.fromEmail.search(filterRegex) !== -1 ||
          record.dateAdded.search(filterRegex) !== -1
        )
      );
    }
    await dispatch(filterRecordsAction(filteredRecords));
    await dispatch(setFiltersActiveAction(filtersActive));
  };
}
