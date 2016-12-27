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
    const tabs = analytics.navigation.map((tab, i) => {
      return (
        <Tab key={i} tabData={tab}>
          <TabsPanel panelData={tab}>
            <ChartContainer chartData={tab} />
            <TableContainer tableData={tab} />
          </TabsPanel>
        </Tab>
      );
    });
    return (
      <div id="tabbed">
        {tabs}
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
