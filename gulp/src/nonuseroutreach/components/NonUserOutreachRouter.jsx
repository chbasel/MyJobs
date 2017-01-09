import React from 'react';
import {Router, Route, IndexRedirect, hashHistory} from 'react-router';
import NonUserOutreachApp from './NonUserOutreachApp';
import OverviewPage from './OverviewPage';
import InboxManagementPage from './InboxManagementPage';
import OutreachRecordPage from './OutreachRecordPage.jsx';
import ProcessRecordPage from './ProcessRecordPage.jsx';

/* NonUserOutreachRouter
 * Component which manages browser history and assigns components to URLs
 */
export default class NonUserOutreachRouter extends React.Component {
  render() {
    return (
      <Router history={hashHistory}>
        <Route path="/" component={NonUserOutreachApp}>
          <IndexRedirect to="/overview" />
          <Route path="/overview" component={OverviewPage} />
          <Route path="/inboxes" component={InboxManagementPage} />
          <Router path="/records" component={OutreachRecordPage} />
          <Router path="/process" component={ProcessRecordPage} />
        </Route>
      </Router>
    );
  }
}
