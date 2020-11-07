import { useState, useCallback } from "react";
import _useWebSocket, { ReadyState } from "react-use-websocket";

const SERVER_URL = "ws://localhost:43968/websocket/";

const MESSAGE = {
  FETCH_MAC_ADDRESSES: "Fetch MAC Addresses",
  GENERATE_DIAGRAM: "Generate Diagram",
};

const useWebSocket = () => {
  // TODO: Send JSON message with data time frame
  const [macAddress, setMacAddress] = useState("default test");
  const [timestampStart, setTimestampStart] = useState(0);
  const [timestampEnd, setTimestampEnd] = useState(0);
  const [macAddresses, setMacAddresses] = useState(["default test"]);
  const [generateDiagramText, setGenerateDiagramText] = useState(
    "Diagram not yet generated"
  );

  const receiveMessage = (event) => {
    const { message, data } = JSON.parse(event.data);

    if (message === MESSAGE.FETCH_MAC_ADDRESSES) setMacAddresses(data);
    else if (message === MESSAGE.GENERATE_DIAGRAM) setGenerateDiagramText(data);
  };

  const {
    sendMessage,
    sendJsonMessage,
    lastMessage,
    lastJsonMessage,
    readyState,
    getWebSocket,
  } = _useWebSocket(SERVER_URL, {
    onMessage: receiveMessage,
  });

  const fetchMacAddresses = useCallback(() => {
    sendMessage(
      JSON.stringify({
        message: MESSAGE.FETCH_MAC_ADDRESSES,
        data: null,
      })
    );
  }, []);

  const generateDiagram = useCallback(() => {
    sendMessage(
      JSON.stringify({
        message: MESSAGE.GENERATE_DIAGRAM,
        data: { macAddress, timestampStart, timestampEnd },
      })
    );
  }, []);

  return {
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
    isOpen: readyState === ReadyState.OPEN,
  };
};

export default useWebSocket;
