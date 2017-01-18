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

    this.toggleMobileMenu = this.toggleMobileMenu.bind(this);
    this.toggleTabsMenu = this.toggleTabsMenu.bind(this);
    this.closeAllMobileMenus = this.closeAllMobileMenus.bind(this);

    this.state = {
      mobileMenuActive: false,
      tabsMenuActive: false,
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
    const currentStartMonth = moment().month() - 1 === -1 ? 11 : moment().month() - 1;
    const currentStartDay = moment().date() + 1;
    const currentStartYear = currentStartMonth === 11 ? moment().year() - 1 : moment().year();
    const {dispatch} = this.props;
    dispatch(doGetPageData(startDate, endDate, currentEndMonth, currentEndDay, currentEndYear, currentStartMonth, currentStartDay, currentStartYear));
  }
  toggleMobileMenu() {
    this.setState({
      mobileMenuActive: !this.state.mobileMenuActive,
    });
  }
  toggleTabsMenu() {
    this.setState({
      tabsMenuActive: !this.state.tabsMenuActive,
    });
  }
  closeAllMobileMenus() {
    this.setState({
      mobileMenuActive: false,
      tabsMenuActive: false,
    });
  }
  render() {
    const {analytics} = this.props;
    console.log(analytics);
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
            <Header tabsActive={this.state.tabsMenuActive} toggleTabs={this.toggleTabsMenu} />
          <div id="page_content" ref="contentContainer">
            <TabsContainer tabsMenuActive={this.state.tabsMenuActive} closeMenus={this.closeAllMobileMenus} />
          </div>
          <div className="clearfix"></div>
        </div>
        <MobileDimensions toggleMenu={this.toggleMobileMenu} activeMobileMenu={this.state.mobileMenuActive} closeMenus={this.closeAllMobileMenus}/>
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
