import React from 'react';
import {connect} from 'react-redux';
import {doGetPageData} from '../actions/page-loading-actions';
import SideBar from './SideBar/SideBar';
import MobileDimensions from './SideBar/MobileDimensions';
import Header from './Header/Header';
import TabsContainer from './Tabs/TabsContainer';
import LoadingSpinner from './Loading';
import moment from 'moment';

class AnalyticsApp extends React.Component {
  constructor() {
    super();

    this.state = {
      mobileActive: false,
    };
  }
  componentDidMount() {
    let startDate = moment();
    const endDate = moment().format('MM/DD/YYYY H:mm:ss');
    startDate = startDate.subtract(30, 'days');
    startDate = startDate.format('MM/DD/YYYY');
    const currentEndMonth = moment().month();
    const currentEndDay = moment().date();
    const currentEndYear = moment().year();
    const currentStartMonth = moment().month() - 1;
    const currentStartDay = moment().date() + 1;
    const currentStartYear = moment().year();
    const {dispatch} = this.props;
    dispatch(doGetPageData(startDate, endDate, currentEndMonth, currentEndDay, currentEndYear, currentStartMonth, currentStartDay, currentStartYear));
  }
  toggleMobileMenu() {
    this.setState({
      mobileActive: !this.state.mobileActive,
    });
  }
  render() {
    const {analytics} = this.props;
    if (analytics.pageFetching) {
      return (
        <LoadingSpinner/>
      );
    }
    return (
      <div>
        <div id="page_wrapper">
            {analytics.navFetching ? <LoadingSpinner/> : ''}
            <SideBar />
            <Header />
          <div id="page_content">
            <TabsContainer/>
          </div>
          <div className="clearfix"></div>
        </div>
        <MobileDimensions toggleMenu={this.toggleMobileMenu.bind(this)} activeMobile={this.state.mobileActive}/>
      </div>
    );
  }
}

AnalyticsApp.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  analytics: React.PropTypes.object.isRequired,
};

export default connect(state => ({
  analytics: state.pageLoadData,
}))(AnalyticsApp);
