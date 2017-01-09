import searchReducer from '../reducers/search-or-add-reducer';
import errorReducer from '../../common/reducers/error-reducer';

import {
  doSearch,
  resetSearchOrAddAction,
} from '../actions/search-or-add-actions';

import {promiseTest} from '../../common/spec';
import IdGenerator from '../../common/id-generator';

import createReduxStore from '../../common/create-redux-store';
import {combineReducers} from 'redux';

class FakeApi {
  search(instance, searchString) {}
}

describe('doSearch', () => {
  let store;
  let idGen;
  let api;

  beforeEach(() => {
    idGen = new IdGenerator();
    api = new FakeApi();
    store = createReduxStore(
      combineReducers({search: searchReducer, error: errorReducer}), {
        search: {
          a: {
            state: 'RESET',
            searchString: 'asdf',
          },
        },
      },
      {idGen, api});
  });

  describe('after a search', () => {
    beforeEach(promiseTest(async () => {
      spyOn(api, 'search').and.callFake(
          (instance, searchString, extraParams) =>
            Promise.resolve([
              'results:' + instance + ' ' +
              searchString, extraParams]));
      // do the search
      await store.dispatch(
        doSearch('a', {1: 2}));
    }));

    it('has search results', () => {
      expect(store.getState().search.a.state).toEqual('RECEIVED');
      expect(store.getState().search.a.results).toDiffEqual([
        'results:a asdf', {1: 2}]);
    });
  });

  describe('after a search api error', () => {
    beforeEach(promiseTest(async () => {
      spyOn(api, 'search').and.throwError(new Error('some error'));
      // do the search
      await store.dispatch(
        doSearch('a'));
    }));

    it('stays loading but records the error', () => {
      expect(store.getState().search.a.state).toEqual('LOADING');
      expect(store.getState().error.lastMessage).toEqual('some error');
    });
  })

});

