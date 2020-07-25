#pragma once

#include "ASL/Tuple.h"

#include <Arduino.h>


/**
 * Class holding a reference to a value which is to be transmitted and a name for the value.
 * 
 * Param:
 *  name: name of the value
 *  ref: value to be transmitted.
 */

template<typename T>
class TrValue
{
public:
	TrValue(String name, T& ref) : name(name), ref(ref) {}

	String name;
	T& ref;
};

/**
 * Parser object used to transmitt TrValue.
 * 
 * Param:
 *  callable: actual parser callable class (lambda!) which takes a name as String and value as any type. It should return a String.
 *  interface: Class with .print() function of type returned by C such as Serial.
 *  head: callable class (lambda!) which is executed at the beginning of each transmittion
 *  foot: callable class (lambda!) which is executed at the end of eacht transmittion
 */

template<typename C, typename I, typename H, typename F>
class TrParser
{
public:
	TrParser(C callable, I& interface, H head, F foot)
     : callable(callable), interface(interface), head(head), foot(foot) {}

	template<typename T>
	void operator()(TrValue<T>& trvalue) const
	{
		interface.print(callable(trvalue.name, trvalue.ref));
	}

	C callable;
    I& interface;
    H head;
    F foot;
};

/**
 * Default Json parser
 */
TrParser JSON_TR_PARSER_DEFAULT(
    [](auto name, auto value) {
        return "\t\"" + name + "\": " + value + ",\n";
    },
    Serial,
    [](){ return String("{\n"); },
    [](){ return String("\t\"time\": " + String(millis()) + "\n}\n"); }
);

/**
 * JsonTransmitter object used to transmitt data sucha as sensor values in (json) format.
 * Format can be customized.
 * 
 * Param:
 *  parser: TrParser such as JSON_TR_PARSER_DEFAULT
 *  args...: arbitrary amount of TrValues to be transmittted
 */

template<template<typename, typename, typename, typename> typename P,
    typename C, typename I, typename H, typename F, typename ... Ts>
class JsonTransmitter
{
public:
	JsonTransmitter(P<C, I, H, F> parser, const Ts& ... args) 
        : parser(parser), interface(parser.interface), attrb(args...) {}

	void transmitt()
	{
        interface.print(parser.head());
		apply(parser, attrb);
        interface.print(parser.foot());
	}

private:
	P<C, I, H, F> parser;
    I& interface;
	Tuple<Ts...> attrb;
};
