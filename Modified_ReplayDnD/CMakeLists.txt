cmake_minimum_required(VERSION 3.14)
project(SokuAI)

add_library(
	AITunnel SHARED
	swrs.h
	ReplayDnD.cpp
)

target_link_libraries(AITunnel shlwapi)

if (MSVC)
else ()
	error("You need to use MSVC to compile this")
endif ()