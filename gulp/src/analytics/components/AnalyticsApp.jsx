import React from 'react';
import {connect} from 'react-redux';
import {doGetPageData} from '../actions/table-filter-actions';
import SideBar from './SideBar/SideBar';
import Header from './Header/Header';
import TabsContainer from './Tabs/TabsContainer';
import LoadingSpinner from './Loading';
import moment from 'moment';

class AnalyticsApp extends React.Component {
  componentDidMount() {
    let startDate = moment();
    const endDate = moment().format('MM/DD/YYYY');
    startDate = startDate.subtract(30, 'days');
    startDate = startDate.format('MM/DD/YYYY');

    const {dispatch, history} = this.props;
    this.unsubscribeToHistory = history.listen(
      (...args) => this.handleNewLocation(...args));

    dispatch(doGetPageData(startDate, endDate));
  }

  componentWillUnmount() {
    this.unsubscribeToHistory();
  }

  async handleNewLocation(_, loc) {
    const {history} = this.props;
    const {state} = loc.location;

    console.log('handleNewLocation', state, history);
  }

  render() {
    const {analytics, history} = this.props;
    if (analytics.fetching) {
      return (
        <LoadingSpinner/>
      );
    }
    return (
      <div id="page_wrapper">
          <SideBar history={history}/>
          <Header/>
        <div id="page_content">
          <TabsContainer/>
        </div>
        <div className="clearfix"></div>
      </div>
    );
  }
}

AnalyticsApp.propTypes = {
  history: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  analytics: React.PropTypes.object.isRequired,
};

export default connect(state => ({
  analytics: state.pageLoadData,
}))(AnalyticsApp);
