import {
  navigationReducer as reducer,
  initialNavigation as state,
} from '../reducers/navigation-reducer';

import {
  setPageAction,
  setWorkflowStateChoicesAction,
  updateTermFilterAction,
  updateWorkflowFilterAction,
  setFiltersActiveAction,
  filterRecordsAction,
} from '../actions/navigation-actions';

describe('navigationReducer', () => {
  describe('setPageAction', () => {
    it('should update tips.', () => {
      const result = reducer(state, setPageAction('records'));
      expect(result.currentPage).toEqual('records');
      expect(result.tips).toEqual([
        'Use this page to view outreach records from non-users.',
      ]);
    });
  });
  describe('setWorkflowStateChoicesAction', () => {
    it('should set workflow state choices', () => {
      const newChoices = [
        {
          value: 'All',
          display: 'All',
          render: () => '',
        },
        {
          value: 'Another',
          display: 'Another',
          render: () => '',
        },
      ]
      const result = reducer(state, setWorkflowStateChoicesAction(newChoices));
      expect(result.workflowChoices).toEqual(newChoices);
    });
  });
  describe('updateTermFilterAction', () => {
    it('should update the current term filter', () => {
      const termFilter = 'blah'
      const result = reducer(state, updateTermFilterAction(termFilter));
      expect(result.termFilter).toEqual(termFilter);
    });
  });
  describe('updateWorkflowFilterAction', () => {
    it('should update the current workflow filter', () => {
      const workflowFilter = 'Active'
      const result = reducer(state, updateWorkflowFilterAction(workflowFilter));
      expect(result.workflowFilter).toEqual(workflowFilter);
    });
  });
  describe('setFiltersActiveAction', () => {
    it('should update whether filters are active', () => {
      const activeFilters = true
      const result = reducer(state, setFiltersActiveAction(activeFilters));
      expect(result.filtersActive).toEqual(activeFilters);
    });
  });
  describe('filterRecordsAction', () => {
    it('should set what records to display', () => {
      const filteredRecords = [{testValue: '1'}, {testValue: '2'}]
      const result = reducer(state, filterRecordsAction(filteredRecords));
      expect(result.filteredRecords).toEqual(filteredRecords);
    });
  });
});

