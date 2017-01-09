import React from 'react';
import ReactDOM from 'react-dom';

import 'babel/polyfill';
import createReduxStore from 'common/create-redux-store';
import {Provider} from 'react-redux';
import {combineReducers} from 'redux';
import {installPolyfills} from 'common/polyfills.js';

import Api from './api';
import {getCsrf} from 'common/cookie';
import {MyJobsApi} from 'common/myjobs-api';
import ManageUsersRouter from './components/ManageUsersRouter';

import confirmReducer, {
  initialConfirmation,
} from 'common/reducers/confirm-reducer';
import loadingReducer, {
  initialLoading,
} from 'common/reducers/loading-reducer';
import activitiesListReducer, {
  initialActivities,
} from './reducers/activities-list-reducer';
import companyReducer, {initialCompany} from './reducers/company-reducer';


installPolyfills();

const reducer = combineReducers({
  activities: activitiesListReducer,
  company: companyReducer,
  confirmation: confirmReducer,
  loading: loadingReducer,
});

const initialState = {
  activities: initialActivities,
  company: initialCompany,
  confirmation: initialConfirmation,
  loading: initialLoading,
};

const myJobsApi = new MyJobsApi(getCsrf());
const api = new Api(myJobsApi);
const thunkExtra = {
  api: api,
};

const store = createReduxStore(reducer, initialState, thunkExtra);

ReactDOM.render((
  <Provider store={store}>
    <ManageUsersRouter />
  </Provider>
), document.getElementById('content'));
