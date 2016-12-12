import React from 'react';
import ReactDOM from 'react-dom';
import {createHistory, useBasename} from 'history';
import {Router, Route} from 'react-router';

import 'babel/polyfill';
import createReduxStore from '../common/create-redux-store';
import {Provider} from 'react-redux';
import {combineReducers} from 'redux';
import {installPolyfills} from '../common/polyfills';

import AnalyticsApp from './components/AnalyticsApp';

import filterReducer, {initialPageData} from './reducers/table-filter-reducer';

import Api from './api';
import {MyJobsApi} from '../common/myjobs-api';
import {getCsrf} from 'common/cookie';

// cross-browser support
installPolyfills();

// Grabbing API class to use for data
const myJobsApi = new MyJobsApi(getCsrf());
const api = new Api(myJobsApi);

// Combining the reducers to make a root reducer
const rootReducer = combineReducers({
  pageLoadData: filterReducer,
});

// Getting the initial state to load into the application
export const initialState = {
  pageLoadData: initialPageData,
};

// Adding thunk for async actions
const thunkExtra = {
  api,
};

// creating the store
const store = createReduxStore(rootReducer, initialState, thunkExtra);

const history = useBasename(createHistory)();

ReactDOM.render(
  <Provider store={store}>
    <Router history={history}>
      <Route path="/" component={AnalyticsApp}/>
    </Router>
  </Provider>
  , document.getElementById('content')
);
