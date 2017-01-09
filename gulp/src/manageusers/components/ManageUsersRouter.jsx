import React from 'react';
import {Router, Route, IndexRoute, hashHistory} from 'react-router';

import Activities from './Activities';
import HelpAndTutorials from './HelpAndTutorials';
import ManageUsersApp from './ManageUsersApp';
import NoMatch from './NoMatch';
import Overview from './Overview';
import Role from './Role';
import Roles from './Roles';
import User from './User';
import Users from './Users';

export default class ManageUsersRouter extends React.Component {
  render() {
    return (
      <Router history={hashHistory}>
        <Route path="/" component={ManageUsersApp}>
          <IndexRoute component={Overview} />
          <Route path="activities" component={Activities} />
          <Route path="roles" component={Roles} />
          <Route path="/role/add" component={Role} />
          <Route path="/role/:roleId" component={Role} />
          <Route path="users" component={Users} />
          <Route path="/user/add" component={User} />
          <Route path="/user/:userId" component={User} />
          <Route path="help-and-tutorials" component={HelpAndTutorials} />
          <Route path="*" component={NoMatch}/>
        </Route>
      </Router>
    );
  }
}
