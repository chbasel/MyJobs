import React, {Component, PropTypes} from 'react';
import {Col, Row} from 'react-bootstrap';
import {connect} from 'react-redux';
import {Loading} from 'common/ui/Loading';
import Menu from './Menu';
import InboxManagementPage from './InboxManagementPage';
import OutreachRecordPage from './OutreachRecordPage';
import ProcessRecordPage from './ProcessRecordPage.jsx';
import OutreachDetails from './OutreachDetails.jsx';
import {markPageLoadingAction} from 'common/actions/loading-actions';
import {doGetInboxes} from '../actions/inbox-actions';
import {doGetRecords} from '../actions/record-actions';
import {
  doLoadEmail,
  markCleanAction,
} from '../actions/process-outreach-actions';
import {setPageAction, doGetWorkflowStateChoices} from '../actions/navigation-actions';
import Confirm from 'common/ui/Confirm';
import {runConfirmInPlace} from 'common/actions/confirm-actions';

/* NonUserOutreachApp
 * An app for managing nonuser outreach, providing a sidebar for navigation and
 * a content area which displays either an overview, inbox management, or
 * outreach record management page.
 */
class NonUserOutreachApp extends Component {
  componentDidMount() {
    const {history} = this.props;
    this.unsubscribeToHistory = history.listen(
      (...args) => this.handleNewLocation(...args));

    this.unsubscribeToListenBefore = history.listenBefore(
      (location, cb) => {
        this.handleBeforeListen(location, cb);
      });
  }

  componentWillUnmount() {
    this.unsubscribeToHistory();
    this.unsubscribeToListenBefore();
  }

  async handleBeforeListen(_location, cb) {
    const {dirty} = this.props;
    if (dirty) {
      const {dispatch} = this.props;
      const message = 'All of your information will be lost if you navigate away from this page.';
      const result = await runConfirmInPlace(dispatch, message);
      if (result) {
        dispatch(markCleanAction());
      }
      cb(result);
    } else {
      cb(true);
    }
  }

  async handleNewLocation(_, loc) {
    const {dispatch} = this.props;
    if (!loc) {
      return;
    }
    const lastComponent = loc.components[loc.components.length - 1];
    if (lastComponent === InboxManagementPage) {
      // update the application's state with the current page and refresh the
      // list of inboxes
      dispatch(setPageAction('inboxes'));
      dispatch(markPageLoadingAction(true));
      await dispatch(doGetInboxes());
      dispatch(markPageLoadingAction(false));
      return;
    } else if (lastComponent === OutreachRecordPage) {
      // update the application's state with the current page and refresh the
      // list of outreach records
      dispatch(markPageLoadingAction(true));
      dispatch(setPageAction('records'));
      await dispatch(doGetRecords());
      await dispatch(doGetWorkflowStateChoices());
      dispatch(markPageLoadingAction(false));
      return;
    } else if (lastComponent === ProcessRecordPage) {
      // update the application's state with the current page and refresh the
      // email
      const recordId = loc.location.query.id;
      dispatch(markPageLoadingAction(true));
      await dispatch(doLoadEmail(recordId));
      dispatch(setPageAction('process'));
      dispatch(markPageLoadingAction(false));
      return;
    }

    // Allow other pages to mount.
    dispatch(markPageLoadingAction(false));
  }

  renderSidebar() {
    const {page, tips} = this.props;

    if (page === 'process') {
      return <OutreachDetails/>;
    }

    return <Menu tips={tips} />;
  }
  render() {
    const {loading} = this.props;
    return (
      <div>
        <Confirm/>
        <Row>
          <Col sm={12}>
            <div className="breadcrumbs">
              <span>
                Non-User Outreach
              </span>
            </div>
          </Col>
        </Row>

        <Row>
          <Col xs={12} md={8}>
            {loading ? <Loading /> : this.props.children}
          </Col>
          <Col xs={12} md={4}>
            {this.renderSidebar()}
          </Col>
        </Row>
      </div>
    );
  }
}

NonUserOutreachApp.propTypes = {
  history: PropTypes.object.isRequired,
  dispatch: PropTypes.func.isRequired,
  // Should we warn the user about losing work if they navigate?
  dirty: PropTypes.bool.isRequired,
  // whether or not to show a page loading indicator in the content area
  loading: PropTypes.bool.isRequired,
  // the tips to pass along to the menu component
  tips: React.PropTypes.arrayOf(React.PropTypes.string.isRequired).isRequired,
  // the current page
  page: React.PropTypes.string.isRequired,
  // which page to show in the content area
  children: PropTypes.node,
};

export default connect(state => ({
  loading: state.loading.mainPage,
  tips: state.navigation.tips,
  page: state.navigation.currentPage,
  dirty: state.process.dirty,
}))(NonUserOutreachApp);
