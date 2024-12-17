import { observer } from "mobx-react-lite";
import "bootstrap/dist/css/bootstrap.css";
import { Form, Button } from "react-bootstrap";
import { Context } from "..";
import { useContext, useEffect, useState } from "react";
import Groups from "./group/Groups";
import VideoGroup from "./group/VideoGroup";
import ChannelGroup from "./group/ChannelGroup";

const Main: React.FC = () => {
  const { store } = useContext(Context);

  const showedElement =
    store.choosed_type === "video" ? (
      <VideoGroup></VideoGroup>
    ) : store.choosed_type === "channel" ? (
      <ChannelGroup></ChannelGroup>
    ) : (
      <Groups></Groups>
    );

  return showedElement;
};

export default observer(Main);
