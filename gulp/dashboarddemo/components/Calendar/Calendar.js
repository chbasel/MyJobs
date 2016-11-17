import React from 'react';
import { Component } from 'react';
import moment from 'moment';
import DateRangePicker from 'react-bootstrap-daterangepicker';
import { Row, Col, Button } from 'react-bootstrap';

class Calendar extends Component {
  constructor(props){
    super(props);
    this.state = {
      ranges: {
      'Today': [moment(), moment()],
      'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
      'Last 7 Days': [moment().subtract(6, 'days'), moment()],
      'Last 30 Days': [moment().subtract(29, 'days'), moment()],
      'This Month': [moment().startOf('month'), moment().endOf('month')],
      'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
    },
      startDate: moment().subtract(29, 'days'),
      endDate: moment()
    }
  }
  handleEvent(event, picker) {
    this.setState({
      startDate: picker.startDate,
      endDate: picker.endDate
    });
  }
  applyDates(event, picker){
    console.log(picker);
  }
  render(){
    var start = this.state.startDate.format('MM-DD-YYYY');
    var end = this.state.endDate.format('MM-DD-YYYY');
    var label = start + ' - ' + end;
    if (start === end) {
      label = start;
    }
    return(
      <div className="container">
        <div className="row">
          <DateRangePicker startDate={this.state.startDate} endDate={this.state.endDate} onApply={this.applyDates.bind(this)} ranges={this.state.ranges} onEvent={this.handleEvent.bind(this)}>
            <Button className="selected-date-range-btn" style={{width:'100%'}}>
              <div className="pull-right">
                <span>
                  {label}
                </span>
                <span className="caret"></span>
              </div>
            </Button>
          </DateRangePicker>
        </div>
      </div>
    );
  }
}

export default Calendar;
