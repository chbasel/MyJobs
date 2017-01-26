import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import {doBreadCrumbSwitchTab} from '../../actions/tab-actions';
import Tab from './Tab';
import TabsPanel from './TabsPanel';
import TableContainer from '../Table/TableContainer';
import ChartContainer from '../Charts/ChartContainer';
import BreadCrumb from '../BreadCrumb';

class TabsContainer extends Component {
  constructor() {
    super();

    this.handleResize = this.handleResize.bind(this);

    this.state = {
      chartWidth: 1,
    };
  }
  componentDidMount() {
    window.addEventListener('resize', this.handleResize);
    this.handleWidth();
  }
  handleResize() {
    this.setState({
      chartWidth: this.refs.contentContainer.clientWidth,
    });
  }
  handleWidth() {
    this.setState({
      chartWidth: this.refs.contentContainer.clientWidth,
    });
  }
  handleBreadcrumbClick(crumb) {
    const {dispatch} = this.props;
    dispatch(doBreadCrumbSwitchTab(crumb));
  }
  render() {
    const {analytics, tabsMenuActive, closeMenus} = this.props;
    const chartWidth = this.state.chartWidth;
    const messageShown = analytics.messageShown;
    const tabsPanel = analytics.navigation.map((tab, index) => {
      return (
        <TabsPanel updatedMessage={messageShown} key={index} id={tab.navId} active={tab.active} label={tab.PageLoadData.column_names[0].label}>
          <BreadCrumb breadcrumbClick={crumb => this.handleBreadcrumbClick(crumb)} id={tab.navId} crumbs={tab.crumbs}/>
          <ChartContainer chartData={tab} width={chartWidth}/>
          <TableContainer tableData={tab}/>
        </TabsPanel>
      );
    });
    return (
      <div ref="contentContainer">
        <Tab active={tabsMenuActive} close={closeMenus}>
          {tabsPanel}
        </Tab>
      </div>
    );
  }
}

TabsContainer.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  analytics: React.PropTypes.object.isRequired,
  /**
   * Boolean stating whether or not the tabs are shown on screen
   */
  tabsMenuActive: React.PropTypes.bool.isRequired,
  /**
   * Function to close all the menus on screen once a tab has been selected
   */
  closeMenus: React.PropTypes.func,
};

export default connect(state => ({
  analytics: state.pageLoadData,
}))(TabsContainer);
