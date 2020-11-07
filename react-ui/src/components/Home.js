import React from "react";

import { Grid, MenuItem, Select, Button } from "@material-ui/core";
import { Refresh, Share } from "@material-ui/icons/";

import useWebsocket from "../hooks/websocket";

function Home() {
  const {
    macAddress,
    setMacAddress,
    timestampStart,
    setTimestampStart,
    timestampEnd,
    setTimestampEnd,
    macAddresses,
    generateDiagramText,
    fetchMacAddresses,
    generateDiagram,
  } = useWebsocket();

  return (
    // TODO: Inputs for datetime start and end
    <Grid
      container
      direction="column"
      justify="space-evenly"
      alignItems="center"
      style={{ width: "auto", height: "auto" }}
    >
      <h2>Select a MAC Address</h2>
      <Grid container justify="space-between" style={{ width: 325 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<Refresh />}
          onClick={fetchMacAddresses}
        >
          Fetch
        </Button>
        <Select
          value={macAddress}
          onChange={(event) => setMacAddress(event.target.value)}
          style={{ minWidth: 215 }}
        >
          {macAddresses.map((value, index) => (
            <MenuItem key={index} value={value}>
              {value}
            </MenuItem>
          ))}
        </Select>
      </Grid>
      <h2>Generate Business Process Diagram</h2>
      <Button
        variant="contained"
        color="primary"
        startIcon={<Share />}
        onClick={generateDiagram}
      >
        Generate
      </Button>
      <p>
        <i>{generateDiagramText}</i>
      </p>
    </Grid>
  );
}

export default Home;
