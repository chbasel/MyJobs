import {promiseTest} from '../../common/spec';
import createReduxStore from '../../common/create-redux-store';
import {
  doRefreshActivities,
} from '../actions/activities-list-actions';
import {combineReducers} from 'redux';
import activitiesListReducer from '../reducers/activities-list-reducer';

class FakeApi {
  getActivities() {}
}

describe('activities-list-actions', () => {
  let store;
  let api;

  beforeEach(promiseTest(async () => {
    api = new FakeApi();

    store = createReduxStore(
      activitiesListReducer,
      undefined,
      {api});
  }));

  describe('doRefreshActivities', () => {
    beforeEach(promiseTest(async () => {
      spyOn(api, 'getActivities').and.returnValue(Promise.resolve({
        MarketPlace: [
          {
            name: "create product",
            description: "Add new products",
            id: 33,
          },
          {
            name: "read product",
            description: "View existing products.",
            id: 34,
          },
        ],
      }))
      await store.dispatch(doRefreshActivities())
    }));

    it('should return activities grouped by app-level access', () => {
      expect(store.getState()).toEqual({
        MarketPlace:  [
          {
            name: "create product",
            description: "Add new products",
            id: 33,
          },
          {
            name: "read product",
            description: "View existing products.",
            id: 34,
          },
        ],
      });
    });
  });
});
