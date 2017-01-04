import React from 'react';
import {Component} from 'react';
import {connect} from 'react-redux';
import Tab from './Tab';
import TabsPanel from './TabsPanel';
import TableContainer from '../Table/TableContainer';
import ChartContainer from '../Charts/ChartContainer';

class TabsContainer extends Component {
  render() {
    const {analytics} = this.props;
    const tabsPanel = analytics.navigation.map((tab, index) => {
      return (
        <TabsPanel key={index} id={tab.navId} active={tab.active} label={tab.PageLoadData.column_names[0].label}>
          <ChartContainer chartData={tab}/>
          <TableContainer tableData={tab}/>
        </TabsPanel>
      );
    });
    return (
      <div>
        <Tab>
          {tabsPanel}
        </Tab>
      </div>
    );
  }
}

TabsContainer.propTypes = {
  analytics: React.PropTypes.object.isRequired,
};

export default connect(state => ({
  analytics: state.pageLoadData,
}))(TabsContainer);
