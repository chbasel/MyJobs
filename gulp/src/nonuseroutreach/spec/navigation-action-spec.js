import {navigationReducer} from '../reducers/navigation-reducer';

import {recordManagementReducer} from '../reducers/record-management-reducer';

import errorReducer from '../../common/reducers/error-reducer';
import {promiseTest} from '../../common/spec';


import {
  doGetWorkflowStateChoices,
  doFilterRecords,
} from '../actions/navigation-actions';

import createReduxStore from '../../common/create-redux-store';
import {combineReducers} from 'redux';

class FakeApi {
  getWorkflowStates() {}
}

describe('doGetWorkflowStateChoices',() => {
  let store;
  let api;

  api = new FakeApi();
  store = createReduxStore(
    combineReducers({navigation: navigationReducer}),
    {}, {api});
  describe('after load', () => {
    beforeEach(promiseTest(async () => {
      expect(store.getState().navigation.workflowChoices.length).toEqual(1);
      spyOn(api, 'getWorkflowStates').and.returnValue(Promise.resolve([{name: 'WF1'}]))
      await store.dispatch(doGetWorkflowStateChoices())
    }));

    it('should have updated choices', () => {
      expect(store.getState().navigation.workflowChoices.length).toEqual(2);
    });
  });
});

describe('doFilterRecords',() => {
  let store;
  let api;
  const testState = {
      records: [
        {
          fromEmail: 'test@test.com',
          outreachEmail: 'detest@my.jobs',
          dateAdded: '06-24-2016',
          currentWorkflowState: 'Newish',
          id: '1',
        },
        {
          fromEmail: 'terribletim@test.com',
          outreachEmail: 'detest@my.jobs',
          dateAdded: '06-24-2011',
          currentWorkflowState: 'Oldish',
          id: '1',
        },
        {
          fromEmail: 'terrantularterry@test.com',
          outreachEmail: 'detest@my.jobs',
          dateAdded: '06-24-2012',
          currentWorkflowState: 'Oldish',
          id: '1',
        },
      ],
      navigation: {
        workflowFilter: 'All',
        termFilter: '',
        filtersActive: false,
        filteredRecords: [],
      }
    };
  const makeStore = (testState) => createReduxStore(
    combineReducers({navigation: navigationReducer, records:recordManagementReducer}),
    testState);

  it('should honor the workflow filter', () => {
    const newState = {
        ...testState,
        navigation: {
          ...testState.navigation,
          workflowFilter: "Oldish",
          filtersActive: true,
        }
      };
    store = makeStore(newState)
    store.dispatch(doFilterRecords());
    expect(store.getState().navigation.filteredRecords.length).toEqual(2);
    });

  it('should honor the term filter', () => {
    const newState = {
        ...testState,
        navigation: {
          ...testState.navigation,
          termFilter: "terribletim",
          filtersActive: true,
        }
      };
    store = makeStore(newState)
    store.dispatch(doFilterRecords());
    expect(store.getState().navigation.filteredRecords.length).toEqual(1);
    });
  });