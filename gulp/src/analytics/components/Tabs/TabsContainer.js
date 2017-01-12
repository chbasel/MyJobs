import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import Tab from './Tab';
import TabsPanel from './TabsPanel';
import TableContainer from '../Table/TableContainer';
import ChartContainer from '../Charts/ChartContainer';

class TabsContainer extends Component {
  constructor() {
    super();

    this.handleResize = this.handleResize.bind(this);
    // this.handleBreadcrumbClick = this.handleBreadcrumbClick.bind(this);

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
  render() {
    const {analytics, tabsMenuActive, closeMenus} = this.props;
    const chartWidth = this.state.chartWidth;
    const tabsPanel = analytics.navigation.map((tab, index) => {
      return (
        <TabsPanel key={index} id={tab.navId} active={tab.active} label={tab.PageLoadData.column_names[0].label}>
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
