import {blendControls} from '../components/util';

describe("blend matching controls", () => {
  it('leaves empty lists alone', () => {
    const result = blendControls([]);
    expect(result).toDiffEqual([]);
  });

  it('leaves controls that cannot be blended alone', () => {
    const controls = [
     {
        ilter: "date_time",
        interface_type: "date_range",
        display: "Date"
      },
      {
        filter: "locations",
        interface_type: "city_state",
        display: "Contact Location"
      },
      {
        filter: "tags",
        interface_type: "tags",
        display: "Tags"
      },
    ];
    const result = blendControls(controls);
    expect(result).toDiffEqual(controls);
  });

  it('blends controls which have the same name', () => {
    const controls = [
      {
        filter: "communication_type",
        interface_type: "search_multiselect",
        display: "Communication Type"
      },
      {
        filter: "partner",
        interface_type: "search_multiselect",
        display: "Partners"
      },
      {
        filter: "contact",
        interface_type: "search_multiselect",
        display: "Contacts"
      },
      {
        filter: "partner_tags",
        interface_type: "tags",
        display: "Partners"
      },
      {
        filter: "contact_tags",
        interface_type: "tags",
        display: "Contacts"
      },
    ];
    const result = blendControls(controls);
    const expected = [
      {
        filter: "communication_type",
        interface_type: "search_multiselect",
        display: "Communication Type"
      },
      {
        interface_type: "composite",
        filter: "partner+partner_tags",
        display: "Partners",
        interfaces: {
          search_multiselect: {
            filter: "partner",
            interface_type: "search_multiselect",
            display: "Partners"
          },
          tags: {
            filter: "partner_tags",
            interface_type: "tags",
            display: "Partners"
          },
        },
      },
      {
        interface_type: "composite",
        filter: "contact+contact_tags",
        display: "Contacts",
        interfaces: {
          "search_multiselect": {
            filter: "contact",
            interface_type: "search_multiselect",
            display: "Contacts"
          },
          "tags": {
            filter: "contact_tags",
            interface_type: "tags",
            display: "Contacts"
          },
        },
      },
    ];
    expect(result).toDiffEqual(expected);

  });
});
